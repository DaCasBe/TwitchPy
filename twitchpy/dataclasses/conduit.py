from dataclasses import dataclass


@dataclass
class Conduit:
    """
    Represents a conduit

    Attributes:
        conduit_id (str): Conduit ID
        shard_count (int): Number of shards associated with this conduit
    """

    conduit_id: str
    shard_count: int
