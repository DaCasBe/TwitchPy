from .._utils import http


def get_content_classification_labels(
    token: str, client_id: str, locale: str = "en-US"
) -> list[dict]:
    url = "https://api.twitch.tv/helix/content_classification_labels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if locale != "en-US":
        params["locale"] = locale

    return http.send_get(url, headers, params)
