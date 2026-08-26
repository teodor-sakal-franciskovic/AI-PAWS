from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.course import Course
from ..models.course_group import CourseGroup
from ..models.course_instructor import CourseInstructor
from ..models.course_student_instructor import CourseStudentInstructor
from ..models.group import Group
from ..models.user import User

from ..schemas.group import GroupUpdate


def retrieve_all_valid(db: Session) -> List[Group]:
    return (
        db.query(Group)
        .filter(Group.is_deleted.is_(False))
        .filter(Group.valid_from <= func.now())
        .filter(Group.valid_until >= func.now())
        .all()
    )


def retrieve_by_id(db: Session, group_id: int) -> Optional[Group]:
    return (
        db.query(Group)
        .filter(Group.id == group_id, Group.is_deleted.is_(False))
        .first()
    )


def name_exists(db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
    query = db.query(Group).filter(
        func.lower(Group.name) == name.lower(), Group.is_deleted.is_(False)
    )
    if exclude_id is not None:
        query = query.filter(Group.id != exclude_id)
    return db.query(query.exists()).scalar()


def retrieve_groups_grouped_by_course(db: Session, user_id: int) -> List[dict]:
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


def update_group(db: Session, group: Group, data: GroupUpdate) -> Group:
    updates = data.model_dump(exclude_unset=True, exclude={"student_ids"})
    for field, value in updates.items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


def link_group_to_course(db: Session, group_id: int, course_id: int) -> None:
    db.add(CourseGroup(course_id=course_id, group_id=group_id))
    db.commit()


def set_students_group(
    db: Session, user_ids: List[int], group_id: Optional[int]
) -> None:
    if not user_ids:
        return
    db.query(User).filter(User.id.in_(user_ids)).update(
        {User.group_id: group_id}, synchronize_session=False
    )
    db.commit()


def retrieve_group_ids_for_course(db: Session, course_id: int) -> List[int]:
    rows = (
        db.query(CourseGroup.group_id)
        .filter(CourseGroup.course_id == course_id)
        .all()
    )
    return [row[0] for row in rows]


def retrieve_unassigned_students_for_course(
    db: Session, course_id: int, group_ids: List[int]
) -> List[User]:
    if not group_ids:
        return []
    assigned_subquery = db.query(CourseStudentInstructor.student_id).filter(
        CourseStudentInstructor.course_id == course_id
    )
    return (
        db.query(User)
        .filter(
            User.group_id.in_(group_ids),
            User.is_active.is_(True),
            ~User.id.in_(assigned_subquery),
        )
        .order_by(User.surname, User.name)
        .all()
    )


def retrieve_already_assigned_student_ids(
    db: Session, course_id: int, student_ids: List[int]
) -> List[int]:
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
    db: Session, course_id: int, student_ids: List[int], instructor_id: int
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


def unassign_students(db: Session, course_id: int, student_ids: List[int]) -> int:
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
) -> List[User]:
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


def retrieve_students_in_group(db: Session, group_id: int) -> List[User]:
    return (
        db.query(User)
        .filter(User.group_id == group_id, User.is_active.is_(True))
        .order_by(User.surname, User.name)
        .all()
    )


def set_user_group(db: Session, user: User, group_id: Optional[int]) -> User:
    user.group_id = group_id
    db.commit()
    db.refresh(user)
    return user
