class Prediction:
    """
    Represents a prediction
    """

    def __init__(
        self,
        prediction_id,
        broadcaster_id,
        broadcaster_name,
        broadcaster_login,
        title,
        winning_outcome_id,
        outcomes,
        prediction_window,
        status,
        created_at,
        ended_at,
        locked_at,
    ):
        """
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

        self.id = prediction_id
        self.broadcaster_id = broadcaster_id
        self.broadcaster_name = broadcaster_name
        self.broadcaster_login = broadcaster_login
        self.title = title
        self.winning_outcome_id = winning_outcome_id
        self.outcomes = outcomes
        self.prediction_window = prediction_window
        self.status = status
        self.created_at = created_at
        self.ended_at = ended_at
        self.locked_at = locked_at
