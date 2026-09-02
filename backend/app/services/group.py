from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.group import Group
from ..repository.course import retrieve_by_id as retrieve_course_by_id
from ..repository.group import (
    add_students_to_group,
    assign_students,
    link_group_to_course,
    name_exists,
    remove_students_from_group,
    repoint_group_students_to_course,
    retrieve_all_valid,
    retrieve_already_assigned_student_ids,
    retrieve_assigned_students_for_instructor,
    retrieve_by_id,
    retrieve_conflicting_group_for_students,
    retrieve_course_id_for_group,
    retrieve_group_ids_for_course,
    retrieve_groups_grouped_by_course,
    retrieve_student_ids_in_course_groups,
    retrieve_student_ids_in_group,
    retrieve_students_in_group,
    retrieve_unassigned_students_for_course,
    set_group_course,
    soft_delete_group,
    unassign_students,
    update_group,
)
from ..repository.role import retrieve_by_name as retrieve_role_by_name
from ..repository.student import retrieve_by_ids as retrieve_students_by_ids
from ..repository.user import retrieve_by_id as retrieve_user_by_id
from ..schemas.audit import AuditResponse
from ..schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupStudentResponse,
    GroupUpdate,
)
from ..services.user import batch_users_for_group
from ..utils.logger import logger


def _validate_student_ids(
    db: Session,
    course_id: int,
    student_ids: list[int],
    exclude_group_id: int | None = None,
) -> None:
    if not student_ids:
        return

    if len(student_ids) != len(set(student_ids)):
        raise ApiError(400, "VALIDATION_ERROR", "Duplicate student IDs in the request.")

    student_role = retrieve_role_by_name(db, "Student")
    users = retrieve_students_by_ids(db, student_ids)
    found_ids = {u.id for u in users}

    missing = set(student_ids) - found_ids
    if missing:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"Student(s) not found: {', '.join(str(i) for i in sorted(missing))}.",
        )

    not_students = [u.id for u in users if u.role_id != student_role.id]
    if not_students:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"User(s) are not students: {', '.join(str(i) for i in sorted(not_students))}.",
        )

    conflicts = retrieve_conflicting_group_for_students(
        db, course_id, student_ids, exclude_group_id=exclude_group_id
    )
    if conflicts:
        raise ApiError(
            409,
            "STUDENT_ALREADY_IN_COURSE_GROUP",
            "One or more students already belong to another group in this course.",
            data={"student_ids": sorted(conflicts.keys())},
        )


def create_group(group: GroupCreate, db: Session, user_id: int) -> int:
    if name_exists(db, group.name):
        raise ApiError(
            409, "GROUP_NAME_ALREADY_EXISTS", "A group with this name already exists."
        )
    if not retrieve_course_by_id(db, group.course_id):
        raise ApiError(400, "VALIDATION_ERROR", "Course not found.")
    _validate_student_ids(db, group.course_id, group.student_ids)

    try:
        logger.info(f"Creating a group with the received object: {group} ")
        db_group = Group(
            name=group.name,
            short_name=group.short_name,
            valid_from=group.valid_from,
            valid_until=group.valid_until,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(db_group)
        db.flush()

        link_group_to_course(db, db_group.id, group.course_id)
        add_students_to_group(db, db_group.id, group.course_id, group.student_ids)

        db.commit()
        db.refresh(db_group)
    except IntegrityError:
        db.rollback()
        raise ApiError(
            409,
            "STUDENT_ALREADY_IN_COURSE_GROUP",
            "One or more students already belong to another group in this course.",
        )
    except Exception as e:
        db.rollback()
        logger.info(
            f"An expection occurred while storing the group {group} to the database: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while storing the group to the database.",
        )
    logger.info(f"Successfully created the group: {db_group}")

    return db_group.id


def retrieve_active_groups(db: Session) -> list[GroupResponse]:
    groups: list[Group] = retrieve_all_valid(db)
    return [
        GroupResponse(
            id=group.id,
            name=group.name,
            short_name=group.short_name,
            valid_from=group.valid_from,
            valid_until=group.valid_until,
        )
        for group in groups
    ]


def get_groups_for_instructor(db: Session, user_id: int) -> list[dict]:
    return retrieve_groups_grouped_by_course(db, user_id)


def _audit(db: Session, entity) -> AuditResponse:
    return AuditResponse(
        created_at=entity.created_at,
        created_by=retrieve_user_by_id(db, entity.created_by)
        if entity.created_by
        else None,
        updated_at=entity.updated_at,
        updated_by=retrieve_user_by_id(db, entity.updated_by)
        if entity.updated_by
        else None,
    )


def get_group_detail(db: Session, group_id: int) -> dict:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise ApiError(404, "GROUP_NOT_FOUND", "Student group not found.")

    course_id = retrieve_course_id_for_group(db, group_id)
    course = retrieve_course_by_id(db, course_id) if course_id else None
    students = retrieve_students_in_group(db, group_id)

    return {
        "id": group.id,
        "name": group.name,
        "short_name": group.short_name,
        "valid_from": group.valid_from,
        "valid_until": group.valid_until,
        "course_id": course.id if course else None,
        "course_name": course.name if course else None,
        "students": [GroupStudentResponse.model_validate(s) for s in students],
        "audit": _audit(db, group),
    }


def modify_group(db: Session, group_id: int, data: GroupUpdate, user_id: int) -> Group:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise ApiError(404, "GROUP_NOT_FOUND", "Group not found.")
    if data.name is not None and name_exists(db, data.name, exclude_id=group_id):
        raise ApiError(
            409, "GROUP_NAME_ALREADY_EXISTS", "A group with this name already exists."
        )

    target_course_id = data.course_id
    if target_course_id is not None:
        if not retrieve_course_by_id(db, target_course_id):
            raise ApiError(400, "VALIDATION_ERROR", "Course not found.")
    else:
        target_course_id = retrieve_course_id_for_group(db, group_id)

    target_student_ids = (
        data.student_ids
        if data.student_ids is not None
        else retrieve_student_ids_in_group(db, group_id)
    )

    if data.course_id is not None or data.student_ids is not None:
        _validate_student_ids(
            db, target_course_id, target_student_ids, exclude_group_id=group_id
        )

    try:
        if data.course_id is not None:
            set_group_course(db, group_id, data.course_id)
            # Keep the denormalized course_id on existing membership rows in
            # sync with the group's new course, even for members not touched
            # by a student_ids diff below.
            repoint_group_students_to_course(db, group_id, data.course_id)

        if data.student_ids is not None:
            current_ids = set(retrieve_student_ids_in_group(db, group_id))
            new_ids = set(data.student_ids)
            to_remove = current_ids - new_ids
            to_add = new_ids - current_ids
            if to_remove:
                remove_students_from_group(db, group_id, list(to_remove))
            if to_add:
                add_students_to_group(db, group_id, target_course_id, list(to_add))

        update_group(db, group, data, user_id)
        db.commit()
        db.refresh(group)
    except IntegrityError:
        db.rollback()
        raise ApiError(
            409,
            "STUDENT_ALREADY_IN_COURSE_GROUP",
            "One or more students already belong to another group in this course.",
        )

    return group


def remove_group(db: Session, group_id: int) -> None:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise ApiError(404, "GROUP_NOT_FOUND", "Group not found.")
    soft_delete_group(db, group)


def _get_group_or_404(db: Session, group_id: int) -> Group:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found."
        )
    return group


def get_students_in_group(db: Session, group_id: int) -> list[GroupStudentResponse]:
    _get_group_or_404(db, group_id)
    students = retrieve_students_in_group(db, group_id)
    return [GroupStudentResponse.model_validate(s) for s in students]


def move_student_to_group(db: Session, group_id: int, user_id: int) -> None:
    _get_group_or_404(db, group_id)
    user = retrieve_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    course_id = retrieve_course_id_for_group(db, group_id)
    if course_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group is not linked to a course.",
        )

    conflicts = retrieve_conflicting_group_for_students(
        db, course_id, [user_id], exclude_group_id=group_id
    )
    if user_id in conflicts:
        remove_students_from_group(db, conflicts[user_id], [user_id])

    if user_id not in retrieve_student_ids_in_group(db, group_id):
        add_students_to_group(db, group_id, course_id, [user_id])
    db.commit()


def remove_student_from_group(db: Session, group_id: int, user_id: int) -> None:
    _get_group_or_404(db, group_id)
    user = retrieve_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    if user_id not in retrieve_student_ids_in_group(db, group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not belong to this group.",
        )
    remove_students_from_group(db, group_id, [user_id])
    db.commit()


def import_students_into_group(db: Session, group_id: int, file: UploadFile) -> int:
    _get_group_or_404(db, group_id)
    course_id = retrieve_course_id_for_group(db, group_id)
    if course_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group is not linked to a course.",
        )
    return batch_users_for_group(file, group_id, course_id, db)


def get_assigned_students_for_instructor(
    db: Session, course_id: int, instructor_id: int
) -> list[GroupStudentResponse]:
    students = retrieve_assigned_students_for_instructor(db, course_id, instructor_id)
    return [GroupStudentResponse.model_validate(s) for s in students]


def _require_course(db: Session, course_id: int) -> None:
    if not retrieve_course_by_id(db, course_id):
        raise ApiError(404, "COURSE_NOT_FOUND", "Course not found.")


def get_unassigned_students_for_course(
    db: Session, course_id: int
) -> list[GroupStudentResponse]:
    """Unassigned students across every group linked to this course, not just one."""
    _require_course(db, course_id)
    group_ids = retrieve_group_ids_for_course(db, course_id)
    students = retrieve_unassigned_students_for_course(db, course_id, group_ids)
    return [GroupStudentResponse.model_validate(s) for s in students]


def assign_students_to_instructor_for_course(
    db: Session, course_id: int, student_ids: list[int], instructor_id: int
) -> None:
    _require_course(db, course_id)

    found_ids = set(retrieve_student_ids_in_course_groups(db, course_id, student_ids))
    not_in_course = [sid for sid in student_ids if sid not in found_ids]
    if not_in_course:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"Student(s) not in any group of this course: {', '.join(str(i) for i in not_in_course)}.",
        )

    already_assigned = retrieve_already_assigned_student_ids(db, course_id, student_ids)
    if already_assigned:
        raise ApiError(
            409,
            "STUDENT_ALREADY_ASSIGNED",
            f"Student(s) already assigned to an instructor for this course: {', '.join(str(i) for i in already_assigned)}.",
        )

    assign_students(db, course_id, student_ids, instructor_id)


def unassign_students_from_instructor_for_course(
    db: Session, course_id: int, student_ids: list[int]
) -> None:
    _require_course(db, course_id)
    assigned = set(retrieve_already_assigned_student_ids(db, course_id, student_ids))
    not_assigned = [sid for sid in student_ids if sid not in assigned]
    if not_assigned:
        raise ApiError(
            404,
            "ASSIGNMENT_NOT_FOUND",
            f"Student(s) have no instructor assigned for this course: {', '.join(str(i) for i in not_assigned)}.",
        )
    unassign_students(db, course_id, student_ids)
