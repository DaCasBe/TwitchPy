class TwitchPyBException(Exception):
    """
    Base exception class for TwitchPy
    """

    def __init__(self,message):
        super().__init__(message)

class InvalidCodeError(TwitchPyBException):
    """
    Exception raised when an invalid code for getting a user token is specified
    """

    def __init__(self,message):
        super().__init__(message)

class UserTokenError(TwitchPyBException):
    """
    Exception raised when a function that requires an user token is called without an user token
    """

    def __init__(self,message):
        super().__init__(message)

class ClientError(TwitchPyBException):
    def __init__(self,message):
        super().__init__(message)

class TooManyArgumentsError(TwitchPyBException):
    def __init__(self,message):
        super().__init__(message)

class FewArgumentsError(TwitchPyBException):
    def __init__(self,message):
        super().__init__(message)