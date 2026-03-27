from datetime import datetime

from .._utils import date, http
from ..dataclasses import SharedChatSession


async def get_shared_chat_session(
    token: str, client_id: str, broadcaster_id: str
) -> SharedChatSession:
    url = "https://api.twitch.tv/helix/shared_chat/session"
    headers = {"Authorization": f"Bearer {token}", "Client-Id": client_id}
    params = {"broadcaster_id": broadcaster_id}

    session = (await http.send_get(url, headers=headers, params=params))[0]

    return SharedChatSession(
        session["session_id"],
        session["host_broadcaster_id"],
        [participant["broadcaster_id"] for participant in session["participants"]],
        datetime.strptime(session["created_at"], date.RFC3339_FORMAT),
        datetime.strptime(session["updated_at"], date.RFC3339_FORMAT),
    )
