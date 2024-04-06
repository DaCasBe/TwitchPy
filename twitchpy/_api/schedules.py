from .._utils import http
from ..dataclasses import StreamSchedule

ENDPOINT_SEGMENTS = "https://api.twitch.tv/helix/schedule/segment"


def get_channel_stream_schedule(
    token: str,
    client_id: str,
    broadcaster_id: str,
    stream_segment_id: list[str] | None = None,
    start_time: str = "",
    utc_offset: str = "0",
    first: int = 20,
) -> list[StreamSchedule]:
    url = "https://api.twitch.tv/helix/schedule"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if stream_segment_id is not None and len(stream_segment_id) > 0:
        params["id"] = stream_segment_id

    if start_time != "":
        params["start_time"] = start_time

    if utc_offset != "0":
        params["utc_offset"] = utc_offset

    schedules = http.send_get_with_pagination(url, headers, params, first, 25)

    return [
        StreamSchedule(
            schedule["segments"],
            schedule["broadcaster_id"],
            schedule["broadcaster_name"],
            schedule["broadcaster_login"],
            schedule["vacation"],
        )
        for schedule in schedules
    ]


def get_channel_icalendar(broadcaster_id: str) -> str:
    """
    Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar

    Args:
        broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule

    Returns:
        str
    """

    url = "https://api.twitch.tv/helix/schedule/icalendar"
    params = {"broadcaster_id": broadcaster_id}

    return http.send_get_text(url, params)


def update_channel_stream_schedule(
    token: str,
    client_id: str,
    broadcaster_id: str,
    is_vacation_enabled: bool = False,
    vacation_start_time: str = "",
    vacation_end_time: str = "",
    timezone: str = "",
) -> None:
    url = "https://api.twitch.tv/helix/schedule/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id

    if is_vacation_enabled:
        data["is_vacation_enabled"] = True

    if vacation_start_time != "":
        data["vacation_start_time"] = vacation_start_time

    if vacation_end_time != "":
        data["vacation_end_time"] = vacation_end_time

    if timezone != "":
        data["timezone"] = timezone

    http.send_patch(url, headers, data)


def create_channel_stream_schedule_segment(
    token: str,
    client_id: str,
    broadcaster_id: str,
    start_time: str,
    timezone: str,
    is_recurring: bool,
    duration: int = 240,
    category_id: str = "",
    title: str = "",
) -> StreamSchedule:
    url = ENDPOINT_SEGMENTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "start_time": start_time,
        "timezone": timezone,
        "is_recurring": is_recurring,
    }

    if duration != 240:
        payload["duration"] = duration

    if category_id != "":
        payload["category_id"] = category_id

    if title != "":
        payload["title"] = title

    schedule = http.send_post_get_result(url, headers, payload)[0]

    return StreamSchedule(
        schedule["segments"],
        schedule["broadcaster_id"],
        schedule["broadcaster_name"],
        schedule["broadcaster_login"],
        schedule["vacation"],
    )


def update_channel_stream_schedule_segment(
    token: str,
    client_id: str,
    broadcaster_id: str,
    stream_segment_id: str,
    start_time: str = "",
    duration: int = 240,
    category_id: str = "",
    title: str = "",
    is_canceled: bool = False,
    timezone: str = "",
) -> StreamSchedule:
    url = ENDPOINT_SEGMENTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id
    data["id"] = stream_segment_id

    if start_time != "":
        data["start_time"] = start_time

    if duration != 240:
        data["duration"] = duration

    if category_id != "":
        data["category_id"] = category_id

    if title != "":
        data["title"] = title

    if is_canceled is not False:
        data["is_canceled"] = is_canceled

    if timezone != "":
        data["timezone"] = timezone

    schedule = http.send_patch_get_result(url, headers, data)[0]

    return StreamSchedule(
        schedule["segments"],
        schedule["broadcaster_id"],
        schedule["broadcaster_name"],
        schedule["broadcaster_login"],
        schedule["vacation"],
    )


def delete_channel_stream_schedule_segment(
    token: str, client_id: str, broadcaster_id: str, stream_segment_id: str
) -> None:
    url = ENDPOINT_SEGMENTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "id": stream_segment_id}

    http.send_delete(url, headers, data)
