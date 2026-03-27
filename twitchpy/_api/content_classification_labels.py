from .._utils import http
from ..dataclasses import ContentClassificationLabel


async def get_content_classification_labels(
    token: str, client_id: str, locale: str = "en-US"
) -> list[ContentClassificationLabel]:
    url = "https://api.twitch.tv/helix/content_classification_labels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
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
