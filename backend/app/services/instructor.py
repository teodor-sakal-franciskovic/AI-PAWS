from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..repository.course import retrieve_courses_for_instructor
from ..repository.group import retrieve_assigned_student_counts
from ..repository.submission import retrieve_latest_completed_evaluative_for_instructor
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)


def _course_stats(course, student_count: int, rows: list, now: datetime) -> dict:
    ungraded = [row for row in rows if not row.graded]
    return {
        "id": course.id,
        "name": course.name,
        "student_count": student_count,
        "students_without_submissions_count": student_count
        - len({row.user_id for row in rows}),
        "completed_submissions_count": len(rows),
        "graded_submissions_count": len(rows) - len(ungraded),
        "ungraded_submissions_count": len(ungraded),
        "longest_waiting_days": max(
            ((now - row.submitted_at).days for row in ungraded), default=0
        ),
    }


def get_instructor_dashboard(db: Session, instructor_id: int) -> dict:
    courses = sorted(
        retrieve_courses_for_instructor(db, instructor_id), key=lambda course: course.id
    )
    course_ids = [course.id for course in courses]
    student_counts = retrieve_assigned_student_counts(db, course_ids, instructor_id)
    evaluative_mode = retrieve_submission_mode_by_name(db, "Evaluative mode")

    rows_by_course: dict[int, list] = {}
    for row in retrieve_latest_completed_evaluative_for_instructor(
        db, course_ids, instructor_id, evaluative_mode.id
    ):
        rows_by_course.setdefault(row.course_id, []).append(row)

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    course_stats = [
        _course_stats(
            course,
            student_counts.get(course.id, 0),
            rows_by_course.get(course.id, []),
            now,
        )
        for course in courses
    ]
    return {
        "summary": {
            "enrollments_count": sum(c["student_count"] for c in course_stats),
            "active_course_count": len(course_stats),
            "ungraded_submissions_count": sum(
                c["ungraded_submissions_count"] for c in course_stats
            ),
            "longest_waiting_days": max(
                (c["longest_waiting_days"] for c in course_stats), default=0
            ),
        },
        "courses": course_stats,
    }
