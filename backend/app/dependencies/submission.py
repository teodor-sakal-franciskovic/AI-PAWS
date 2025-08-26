from ..services.submission import (
    save_submission,
    retrieve_submission,
    update_submission_status,
)


def get_save_submission():
    return save_submission


def get_retrieve_submission():
    return retrieve_submission


def get_update_submission_status():
    return update_submission_status
