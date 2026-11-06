from sqlalchemy.orm import Session

from ..models.user_course_points import UserCoursePoints


def retrieve_course_points(
    db: Session, course_id: int, user_ids: list[int]
) -> dict[int, UserCoursePoints]:
    if not user_ids:
        return {}
    rows = (
        db.query(UserCoursePoints)
        .filter(
            UserCoursePoints.course_id == course_id,
            UserCoursePoints.user_id.in_(user_ids),
        )
        .all()
    )
    return {row.user_id: row for row in rows}


def save_user_course_points(
    db: Session,
    course_id: int,
    user_id: int,
    achieved_points: float,
    max_points: float,
) -> UserCoursePoints:
    row = db.get(UserCoursePoints, (course_id, user_id))
    if row is None:
        row = UserCoursePoints(course_id=course_id, user_id=user_id)
        db.add(row)
    row.achieved_points = achieved_points
    row.max_points = max_points
    db.flush()
    return row
