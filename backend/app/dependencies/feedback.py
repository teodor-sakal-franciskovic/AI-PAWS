from ..services.feedback import (
    request_initial_interactive_feedback,
    request_additional_interactive_feedback,
    create_feedback_objects_for_interactive_mode,
    retrieve_feedback,
    update_feedback_with_additional_context,
    request_evaluation,
    create_feedback_objects_for_evaluative_mode,
)


def get_request_initial_interactive_feedback():
    return request_initial_interactive_feedback


def get_request_additional_interactive_feedback():
    return request_additional_interactive_feedback


def get_create_feedback_objects_for_interactive_mode():
    return create_feedback_objects_for_interactive_mode


def get_retrieve_feedback():
    return retrieve_feedback


def get_update_feedback_with_additional_text():
    return update_feedback_with_additional_context


def get_request_evaluation():
    return request_evaluation


def get_create_feedback_objects_for_evaluative_mode():
    return create_feedback_objects_for_evaluative_mode
