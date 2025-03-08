from dataclasses import dataclass


@dataclass
class TokenInfo:
    """
    Represents the token validity

    Attributes:
        client_id (str): The authenticated client ID
        login (str): The username of the authenticated client
        scopes (list[str]): The list of scopes authorized for use by the client
        user_id (str): The user ID of the authenticated client
        expires_in (int): Number of seconds until the token expires
    """
    client_id: str
    login: str
    scopes: list[str]
    user_id: str
    expires_in: int
