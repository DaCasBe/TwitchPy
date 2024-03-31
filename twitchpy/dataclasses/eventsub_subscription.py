class EventSubSubscription:
    """
    Represents an EventSub subscription
    """

    def __init__(
        self,
        subscription_id,
        status,
        subscription_type,
        version,
        condition,
        created_at,
        transport,
        cost,
    ):
        """
        Args:
            id (str): An ID that identifies the subscription
            status (str): The subscription’s status
                          Possible values are: enabled, webhook_callback_verification_pending, webhook_callback_verification_failed, notification_failures_exceeded, authorization_revoked, user_removed
            type (str): The subscription’s type
            version (str): The version of the subscription type
            condition (dict): The subscription’s parameter values
            created_at (str): The RFC 3339 timestamp indicating when the subscription was created
            transport (dict): The transport details used to send you notifications
            cost (int): The amount that the subscription counts against your limit
        """

        self.id = subscription_id
        self.status = status
        self.type = subscription_type
        self.version = version
        self.condition = condition
        self.created_at = created_at
        self.transport = transport
        self.cost = cost
