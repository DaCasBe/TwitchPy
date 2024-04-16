from dataclasses import dataclass

from ..dataclasses import Transport


@dataclass
class ConduitShard:
    """
    Represents a conduit's shard

    Attributes:
        shard_id (str): Shard ID
        status (str): The shard status
            Possible values: enabled, webhook_callback_verification_pending, webhook_callback_verification_failed, notification_failures_exceeded, websocket_disconnected, websocket_failed_ping_pong, websocket_received_inbound_traffic, websocket_internal_error, websocket_network_timeout, websocket_network_error, websocket_failed_to_reconnect
        transport (Transport): The transport details used to send the notifications
    """

    shard_id: str
    status: str
    transport: Transport
