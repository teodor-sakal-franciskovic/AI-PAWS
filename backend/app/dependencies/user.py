from ..services.user import (
    batch_users,
    create_user,
    deactivate_user,
    retrieve_logged_in_user,
    update_user_info,
    update_user_password,
)


def get_create_user():
    return create_user


def get_retrieve_logged_in_user():
    return retrieve_logged_in_user


def get_update_user_info():
    return update_user_info


def get_update_user_password():
    return update_user_password


def get_deactivate_user():
    return deactivate_user


def get_batch_users():
    return batch_users
