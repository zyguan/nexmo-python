__all__ = ["ClientError", "ServerError", "AuthenticationError"]


class Error(Exception):
    pass


class ClientError(Error):
    pass


class ServerError(Error):
    pass


class AuthenticationError(ClientError):
    pass
