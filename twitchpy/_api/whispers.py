from .._utils import http


class WhispersAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def send_whisper(
        self, from_user_id: str, to_user_id: str, message: str
    ) -> None:
        url = "https://api.twitch.tv/helix/whispers"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": "application/json",
        }
        payload = {
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "message": message,
        }

        await http.send_post(url, headers, payload)
