from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, Game, StreamSchedule, StreamScheduleSegment, User

ENDPOINT_SEGMENTS = "https://api.twitch.tv/helix/schedule/segment"


def get_channel_stream_schedule(
    token: str,
    client_id: str,
    broadcaster_id: str,
    stream_segment_id: list[str] | None = None,
    start_time: datetime | None = None,
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

    if start_time is not None:
        params["start_time"] = start_time

    schedules = http.send_get_with_pagination(url, headers, params, first, 25)

    return [
        StreamSchedule(
            [
                StreamScheduleSegment(
                    segment["id"],
                    datetime.strptime(segment["start_time"], date.RFC3339_FORMAT),
                    datetime.strptime(segment["end_time"], date.RFC3339_FORMAT),
                    segment["title"],
                    datetime.strptime(segment["canceled_until"], date.RFC3339_FORMAT),
                    Game(segment["category"]["id"], segment["category"]["name"]),
                    segment["is_recurring"],
                )
                for segment in schedule["segments"]
            ],
            Channel(
                User(
                    schedule["broadcaster_id"],
                    schedule["broadcaster_login"],
                    schedule["broadcaster_name"],
                )
            ),
            (
                datetime.strptime(
                    schedule["vacation"]["start_time"], date.RFC3339_FORMAT
                ),
                datetime.strptime(
                    schedule["vacation"]["end_time"], date.RFC3339_FORMAT
                ),
            ),
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
    is_vacation_enabled: bool | None = None,
    vacation_start_time: datetime | None = None,
    vacation_end_time: datetime | None = None,
    timezone: str | None = None,
) -> None:
    url = "https://api.twitch.tv/helix/schedule/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id

    if is_vacation_enabled is not None:
        data["is_vacation_enabled"] = is_vacation_enabled

    if vacation_start_time is not None:
        data["vacation_start_time"] = vacation_start_time

    if vacation_end_time is not None:
        data["vacation_end_time"] = vacation_end_time

    if timezone is not None:
        data["timezone"] = timezone

    http.send_patch(url, headers, data)


def create_channel_stream_schedule_segment(
    token: str,
    client_id: str,
    broadcaster_id: str,
    start_time: datetime,
    timezone: str,
    is_recurring: bool,
    duration: int = 240,
    category_id: str | None = None,
    title: str | None = None,
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
        "duration": duration,
    }

    if category_id is not None:
        payload["category_id"] = category_id

    if title is not None:
        payload["title"] = title

    schedule = http.send_post_get_result(url, headers, payload)[0]

    return StreamSchedule(
        [
            StreamScheduleSegment(
                segment["id"],
                datetime.strptime(segment["start_time"], date.RFC3339_FORMAT),
                datetime.strptime(segment["end_time"], date.RFC3339_FORMAT),
                segment["title"],
                datetime.strptime(segment["canceled_until"], date.RFC3339_FORMAT),
                Game(segment["category"]["id"], segment["category"]["name"]),
                segment["is_recurring"],
            )
            for segment in schedule["segments"]
        ],
        Channel(
            User(
                schedule["broadcaster_id"],
                schedule["broadcaster_login"],
                schedule["broadcaster_name"],
            )
        ),
        (
            datetime.strptime(schedule["vacation"]["start_time"], date.RFC3339_FORMAT),
            datetime.strptime(schedule["vacation"]["end_time"], date.RFC3339_FORMAT),
        ),
    )


def update_channel_stream_schedule_segment(
    token: str,
    client_id: str,
    broadcaster_id: str,
    stream_segment_id: str,
    start_time: datetime | None = None,
    duration: int | None = None,
    category_id: str | None = None,
    title: str | None = None,
    is_canceled: bool | None = None,
    timezone: str | None = None,
) -> StreamSchedule:
    url = ENDPOINT_SEGMENTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id
    data["id"] = stream_segment_id

    if start_time is not None:
        data["start_time"] = start_time

    if duration is not None:
        data["duration"] = duration

    if category_id is not None:
        data["category_id"] = category_id

    if title is not None:
        data["title"] = title

    if is_canceled is not None:
        data["is_canceled"] = is_canceled

    if timezone is not None:
        data["timezone"] = timezone

    schedule = http.send_patch_get_result(url, headers, data)[0]

    return StreamSchedule(
        [
            StreamScheduleSegment(
                segment["id"],
                datetime.strptime(segment["start_time"], date.RFC3339_FORMAT),
                datetime.strptime(segment["end_time"], date.RFC3339_FORMAT),
                segment["title"],
                datetime.strptime(segment["canceled_until"], date.RFC3339_FORMAT),
                Game(segment["category"]["id"], segment["category"]["name"]),
                segment["is_recurring"],
            )
            for segment in schedule["segments"]
        ],
        Channel(
            User(
                schedule["broadcaster_id"],
                schedule["broadcaster_login"],
                schedule["broadcaster_name"],
            )
        ),
        (
            datetime.strptime(schedule["vacation"]["start_time"], date.RFC3339_FORMAT),
            datetime.strptime(schedule["vacation"]["end_time"], date.RFC3339_FORMAT),
        ),
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
