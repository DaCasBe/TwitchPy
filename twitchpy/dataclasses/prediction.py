from dataclasses import dataclass


@dataclass
class Prediction:
    """
    Represents a prediction

    Args:
        prediction_id (str): ID of the Prediction
        broadcaster_id (str): ID of the broadcaster
        broadcaster_name (str): Name of the broadcaster
        broadcaster_login (str): Login of the broadcaster
        title (str): Title for the Prediction
        winning_outcome_id (str): ID of the winning outcome
            If the status is ACTIVE, this is set to null
        outcomes (list): Possible outcomes for the Prediction
        prediction_window (int): Total duration for the Prediction (in seconds)
        status (str): Status of the Prediction
            Valid values are: RESOLVED, ACTIVE, CANCELED, LOCKED
        created_at (str): UTC timestamp for the Prediction’s start time
        ended_at (str): UTC timestamp for when the Prediction ended
            If the status is ACTIVE, this is set to null
        locked_at (str): UTC timestamp for when the Prediction was locked
            If the status is not LOCKED, this is set to null
    """

    prediction_id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    title: str
    winning_outcome_id: str
    outcomes: list[dict]
    prediction_window: int
    status: str
    created_at: str
    ended_at: str
    locked_at: str
