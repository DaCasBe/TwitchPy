from dataclasses import dataclass

from ..dataclasses import Predictor


@dataclass
class PredictionOutcome:
    """
    Represents an outcome for a prediction

    Attributes:
        outcome_id (str): An ID that identifies this outcome
        title (str): The outcome’s text
        users (int): The number of unique viewers that chose this outcome
        channel_points (int): The number of Channel Points spent by viewers on this outcome
        top_predictors (list[Predictor]): A list of viewers who were the top predictors
        color (str): The color that visually identifies this outcome in the UX
            Possible values: BLUE, PINK
    """

    outcome_id: str
    title: str
    users: int
    channel_points: int
    top_predictors: list[Predictor]
    color: str
