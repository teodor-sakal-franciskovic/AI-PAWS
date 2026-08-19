from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..models.course import Course
from ..models.course_group import CourseGroup
from ..models.course_instructor import CourseInstructor
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
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


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
