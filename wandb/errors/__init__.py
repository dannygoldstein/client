import requests


class Error(Exception):
    """Base W&B Error"""

    def __init__(self, message):
        super(Error, self).__init__(message)
        self.message = message

    # For python 2 support
    def encode(self, encoding):
        return self.message


class CommError(Error):
    """Error communicating with W&B"""

    def __init__(self, msg, exc=None):
        super(CommError, self).__init__(msg)
        self.message = msg
        self.exc = exc


class UsageError(Error):
    """API Usage Error"""

    pass


class LogError(Error):
    """Raised when wandb.log() fails"""

    pass


class LogMultiprocessError(LogError):
    """Raised when wandb.log() fails because of multiprocessing"""

    pass


class RequireError(Error):
    """Raised when wandb.require() fails"""

    pass


__all__ = [
    "Error",
    "UsageError",
    "CommError",
    "LogError",
    "LogMultiprocessError",
    "RequireError",
    "ReadTimeoutWithContext",
]


class ReadTimeoutWithContext(requests.exceptions.ReadTimeout):
    def __init__(
        self,
        read_timeout_exc: requests.exceptions.ReadTimeout,
        timeout: int,
        num_iters: int = 0,
    ):
        self.exc = read_timeout_exc
        self.timeout = timeout
        self.num_iters = num_iters
