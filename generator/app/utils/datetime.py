from datetime import datetime, timezone


def current_time():
    return datetime.now(tz=timezone.utc)
