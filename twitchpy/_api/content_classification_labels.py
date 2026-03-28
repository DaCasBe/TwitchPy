from .._utils import http
from ..dataclasses import ContentClassificationLabel


class ContentClassificationLabelsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_content_classification_labels(
        self, locale: str = "en-US"
    ) -> list[ContentClassificationLabel]:
        url = "https://api.twitch.tv/helix/content_classification_labels"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"locale": locale}

        content_classification_labels = await http.send_get(url, headers, params)

        return [
            ContentClassificationLabel(
                content_classification_label["id"],
                content_classification_label["description"],
                content_classification_label["name"],
            )
            for content_classification_label in content_classification_labels
        ]
