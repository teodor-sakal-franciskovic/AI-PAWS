from ..services.assignment import (
    create_assignment,
    retrieve_active_assignments_for_student,
    retrieve_previous_assignments_for_student,
    retrieve_submission_files_for_assignment,
    retrieve_assignments,
)


def get_create_assignment():
    return create_assignment


def get_retrieve_active_assignments_for_student():
    return retrieve_active_assignments_for_student


def get_retrieve_previous_assignments_for_student():
    return retrieve_previous_assignments_for_student


def get_retrieve_submission_files_for_assignment():
    return retrieve_submission_files_for_assignment


def get_retrieve_assignments():
    return retrieve_assignments
