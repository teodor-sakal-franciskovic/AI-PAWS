from ..services.assignment import (
    create_assignment,
    retrieve_active_assignments_for_student,
    retrieve_previous_assignments_for_student,
)


def get_create_assignment():
    return create_assignment


def get_retrieve_active_assignments_for_student():
    return retrieve_active_assignments_for_student


def get_retrieve_previous_assignments_for_student():
    return retrieve_previous_assignments_for_student
