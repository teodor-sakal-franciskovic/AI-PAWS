from ..services.historical_profile import (
    insert_historical_profile_snapshot,
    retrieve_latest_historical_profile_snapshot,
)


def get_insert_historical_profile_snapshot():
    return insert_historical_profile_snapshot


def get_retrieve_latest_historical_profile_snapshot():
    return retrieve_latest_historical_profile_snapshot
