class TwitchPyBException(Exception):
    """
    Base exception class for TwitchPy
    """

    def __init__(self, message):
        super().__init__(message)


class AppTokenError(TwitchPyBException):
    """
    Exception raised when an error trying to get an app token happens
    """


class UserTokenError(TwitchPyBException):
    """
    Exception raised when a function that requires an user token is called without an user token
    """


class ClientError(TwitchPyBException):
    """
    Exception raised when a bad request is made by a client
    """
