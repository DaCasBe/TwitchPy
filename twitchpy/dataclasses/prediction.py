from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, PredictionOutcome


@dataclass
class Prediction:
    """
    Represents a prediction

    Args:
        prediction_id (str): ID of the Prediction
        channel (Channel): The channel where the prediction was created
        title (str): Title for the Prediction
        winning_outcome_id (str): ID of the winning outcome
            If the status is ACTIVE, this is set to null
        outcomes (list[PredictionOutcome]): Possible outcomes for the Prediction
        prediction_window (int): Total duration for the Prediction (in seconds)
        status (str): Status of the Prediction
            Valid values are: RESOLVED, ACTIVE, CANCELED, LOCKED
        created_at (datetime): UTC timestamp for the Prediction’s start time
        ended_at (datetime): UTC timestamp for when the Prediction ended
            If the status is ACTIVE, this is set to null
        locked_at (datetime): UTC timestamp for when the Prediction was locked
            If the status is not LOCKED, this is set to null
    """

    prediction_id: str
    channel: Channel
    title: str
    winning_outcome_id: str
    outcomes: list[PredictionOutcome]
    prediction_window: int
    status: str
    created_at: datetime
    ended_at: datetime
    locked_at: datetime
