from ..services.group import create_group, retrieve_active_groups


def get_create_group():
    return create_group


def get_retrieve_active_groups():
    return retrieve_active_groups
