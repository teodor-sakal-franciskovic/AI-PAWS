from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.course import Course
from ..models.course_group import CourseGroup
from ..models.course_instructor import CourseInstructor
from ..models.course_student_instructor import CourseStudentInstructor
from ..models.group import Group
from ..models.group_student import GroupStudent
from ..models.user import User
from ..schemas.group import GroupUpdate


def retrieve_all_valid(db: Session) -> list[Group]:
    return (
        db.query(Group)
        .filter(Group.is_deleted.is_(False))
        .filter(Group.valid_from <= func.now())
        .filter(Group.valid_until >= func.now())
        .all()
    )


def retrieve_by_id(db: Session, group_id: int) -> Group | None:
    return (
        db.query(Group)
        .filter(Group.id == group_id, Group.is_deleted.is_(False))
        .first()
    )


def name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    query = db.query(Group).filter(
        func.lower(Group.name) == name.lower(), Group.is_deleted.is_(False)
    )
    if exclude_id is not None:
        query = query.filter(Group.id != exclude_id)
    return db.query(query.exists()).scalar()


def retrieve_groups_grouped_by_course(db: Session, user_id: int) -> list[dict]:
    courses = (
        db.query(Course)
        .outerjoin(CourseInstructor, CourseInstructor.course_id == Course.id)
        .filter(
            or_(
                Course.created_by == user_id,
                CourseInstructor.instructor_id == user_id,
            )
        )
        .distinct()
        .all()
    )

    result = []
    for course in courses:
        groups = (
            db.query(Group)
            .join(CourseGroup, CourseGroup.group_id == Group.id)
            .filter(
                CourseGroup.course_id == course.id,
                Group.is_deleted.is_(False),
            )
            .all()
        )
        result.append(
            {
                "course_id": course.id,
                "course_name": course.name,
                "groups": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "short_name": g.short_name,
                        "valid_from": g.valid_from,
                        "valid_until": g.valid_until,
                    }
                    for g in groups
                ],
            }
        )
    return result


def retrieve_course_id_for_group(db: Session, group_id: int) -> int | None:
    row = (
        db.query(CourseGroup.course_id).filter(CourseGroup.group_id == group_id).first()
    )
    return row[0] if row else None


def link_group_to_course(db: Session, group_id: int, course_id: int) -> None:
    """Links a newly-created group to its course. Caller must commit."""
    db.add(CourseGroup(course_id=course_id, group_id=group_id))


def set_group_course(db: Session, group_id: int, course_id: int) -> None:
    """Replaces whichever course a group is currently linked to. Caller must commit."""
    db.query(CourseGroup).filter(CourseGroup.group_id == group_id).delete(
        synchronize_session=False
    )
    db.add(CourseGroup(course_id=course_id, group_id=group_id))


def update_group(db: Session, group: Group, data: GroupUpdate, user_id: int) -> Group:
    """Updates the group's own fields and audit stamp. Caller must commit.
    Course/membership changes are handled separately since they touch other
    tables and need their own conflict handling."""
    updates = data.model_dump(exclude_unset=True, exclude={"student_ids", "course_id"})
    for field, value in updates.items():
        setattr(group, field, value)
    group.updated_by = user_id
    group.updated_at = func.now()
    return group


def retrieve_group_ids_for_course(db: Session, course_id: int) -> list[int]:
    rows = (
        db.query(CourseGroup.group_id).filter(CourseGroup.course_id == course_id).all()
    )
    return [row[0] for row in rows]


def retrieve_group_ids_for_student(db: Session, student_id: int) -> list[int]:
    rows = (
        db.query(GroupStudent.group_id)
        .filter(GroupStudent.student_id == student_id)
        .all()
    )
    return [row[0] for row in rows]


def retrieve_conflicting_group_for_students(
    db: Session,
    course_id: int,
    student_ids: list[int],
    exclude_group_id: int | None = None,
) -> dict:
    """Maps student_id -> group_id for students already in a *different* group
    of this course (the invariant a student may only be in one group per course)."""
    if not student_ids:
        return {}
    query = db.query(GroupStudent.student_id, GroupStudent.group_id).filter(
        GroupStudent.course_id == course_id,
        GroupStudent.student_id.in_(student_ids),
    )
    if exclude_group_id is not None:
        query = query.filter(GroupStudent.group_id != exclude_group_id)
    return {row.student_id: row.group_id for row in query.all()}


def add_students_to_group(
    db: Session, group_id: int, course_id: int, student_ids: list[int]
) -> None:
    """Caller must commit."""
    for student_id in student_ids:
        db.add(
            GroupStudent(group_id=group_id, student_id=student_id, course_id=course_id)
        )


def repoint_group_students_to_course(
    db: Session, group_id: int, course_id: int
) -> None:
    """Updates the denormalized course_id on a group's existing membership rows,
    e.g. after the group itself is moved to a different course. Caller must commit."""
    db.query(GroupStudent).filter(GroupStudent.group_id == group_id).update(
        {GroupStudent.course_id: course_id}, synchronize_session=False
    )


def remove_students_from_group(
    db: Session, group_id: int, student_ids: list[int]
) -> None:
    """Caller must commit."""
    if not student_ids:
        return
    db.query(GroupStudent).filter(
        GroupStudent.group_id == group_id, GroupStudent.student_id.in_(student_ids)
    ).delete(synchronize_session=False)


def retrieve_student_ids_in_course_groups(
    db: Session, course_id: int, student_ids: list[int]
) -> list[int]:
    """Of the given students, which are in *any* group linked to this course."""
    if not student_ids:
        return []
    rows = (
        db.query(GroupStudent.student_id)
        .filter(
            GroupStudent.course_id == course_id,
            GroupStudent.student_id.in_(student_ids),
        )
        .all()
    )
    return [row[0] for row in rows]


def retrieve_student_ids_in_group(db: Session, group_id: int) -> list[int]:
    rows = (
        db.query(GroupStudent.student_id)
        .filter(GroupStudent.group_id == group_id)
        .all()
    )
    return [row[0] for row in rows]


def retrieve_unassigned_students_for_course(
    db: Session, course_id: int, group_ids: list[int]
) -> list[User]:
    if not group_ids:
        return []
    assigned_subquery = db.query(CourseStudentInstructor.student_id).filter(
        CourseStudentInstructor.course_id == course_id
    )
    member_subquery = db.query(GroupStudent.student_id).filter(
        GroupStudent.group_id.in_(group_ids)
    )
    return (
        db.query(User)
        .filter(
            User.id.in_(member_subquery),
            User.is_active.is_(True),
            ~User.id.in_(assigned_subquery),
        )
        .order_by(User.surname, User.name)
        .all()
    )


def retrieve_already_assigned_student_ids(
    db: Session, course_id: int, student_ids: list[int]
) -> list[int]:
    rows = (
        db.query(CourseStudentInstructor.student_id)
        .filter(
            CourseStudentInstructor.course_id == course_id,
            CourseStudentInstructor.student_id.in_(student_ids),
        )
        .all()
    )
    return [row[0] for row in rows]


def assign_students(
    db: Session, course_id: int, student_ids: list[int], instructor_id: int
) -> None:
    try:
        for student_id in student_ids:
            db.add(
                CourseStudentInstructor(
                    course_id=course_id,
                    student_id=student_id,
                    instructor_id=instructor_id,
                )
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ApiError(
            409,
            "STUDENT_ALREADY_ASSIGNED",
            "One or more students were already assigned to an instructor for this course.",
        )


def unassign_students(db: Session, course_id: int, student_ids: list[int]) -> int:
    deleted = (
        db.query(CourseStudentInstructor)
        .filter(
            CourseStudentInstructor.course_id == course_id,
            CourseStudentInstructor.student_id.in_(student_ids),
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def retrieve_assigned_students_for_instructor(
    db: Session, course_id: int, instructor_id: int
) -> list[User]:
    return (
        db.query(User)
        .join(CourseStudentInstructor, CourseStudentInstructor.student_id == User.id)
        .filter(
            CourseStudentInstructor.course_id == course_id,
            CourseStudentInstructor.instructor_id == instructor_id,
        )
        .order_by(User.surname, User.name)
        .all()
    )


def soft_delete_group(db: Session, group: Group) -> None:
    group.is_deleted = True
    db.commit()


def retrieve_students_in_group(db: Session, group_id: int) -> list[User]:
    return (
        db.query(User)
        .join(GroupStudent, GroupStudent.student_id == User.id)
        .filter(GroupStudent.group_id == group_id, User.is_active.is_(True))
        .order_by(User.surname, User.name)
        .all()
    )
