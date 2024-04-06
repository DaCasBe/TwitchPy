from .._utils import http
from ..dataclasses import Prediction

ENDPOINT_PREDICTIONS = "https://api.twitch.tv/helix/predictions"


def get_predictions(
    token: str,
    client_id: str,
    broadcaster_id: str,
    prediction_ids: list[str] | None = None,
    first: int = 20,
) -> list[Prediction]:
    url = ENDPOINT_PREDICTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if prediction_ids is not None and len(prediction_ids) > 0:
        params["id"] = prediction_ids

    predictions = http.send_get_with_pagination(url, headers, params, first, 20)

    return [
        Prediction(
            prediction["id"],
            prediction["broadcaster_id"],
            prediction["broadcaster_name"],
            prediction["broadcaster_login"],
            prediction["title"],
            prediction["winning_outcome_id"],
            prediction["outcomes"],
            prediction["prediction_window"],
            prediction["status"],
            prediction["created_at"],
            prediction["ended_at"],
            prediction["locked_at"],
        )
        for prediction in predictions
    ]


def create_prediction(
    token: str,
    client_id: str,
    broadcaster_id: str,
    title: str,
    outcomes: list[str],
    prediction_window: int,
) -> Prediction:
    url = ENDPOINT_PREDICTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "title": title,
        "prediction_window": prediction_window,
    }

    outcomes_payload = []

    for outcome in outcomes:
        outcomes_payload.append({"title": outcome})

    payload["outcomes"] = outcomes_payload

    prediction = http.send_post_get_result(url, headers, payload)[0]

    return Prediction(
        prediction["id"],
        prediction["broadcaster_id"],
        prediction["broadcaster_name"],
        prediction["broadcaster_login"],
        prediction["title"],
        prediction["winning_outcome_id"],
        prediction["outcomes"],
        prediction["prediction_window"],
        prediction["status"],
        prediction["created_at"],
        prediction["ended_at"],
        prediction["locked_at"],
    )


def end_prediction(
    token: str,
    client_id: str,
    broadcaster_id: str,
    prediction_id: str,
    status: str,
    winning_outcome_id: str = "",
) -> Prediction:
    url = ENDPOINT_PREDICTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "id": prediction_id, "status": status}

    if winning_outcome_id != "":
        data["winning_outcome_id"] = winning_outcome_id

    prediction = http.send_patch_get_result(url, headers, data)[0]

    return Prediction(
        prediction["id"],
        prediction["broadcaster_id"],
        prediction["broadcaster_name"],
        prediction["broadcaster_login"],
        prediction["title"],
        prediction["winning_outcome_id"],
        prediction["outcomes"],
        prediction["prediction_window"],
        prediction["status"],
        prediction["created_at"],
        prediction["ended_at"],
        prediction["locked_at"],
    )
