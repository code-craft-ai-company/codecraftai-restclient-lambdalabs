"""
    .. module:: lambdalabserrors
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the exception types raised by the
                   Lambda Labs REST client when API calls fail.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


class LambdalabsError(RuntimeError):
    """
        Base class for every Lambda Labs REST client error.
    """


class LambdalabsAuthenticationError(LambdalabsError):
    """
        Raised when the Lambda Labs API rejects the request with HTTP 401
        or 403, indicating an invalid or unauthorised API key.
    """


class LambdalabsInstanceTypeNotFoundError(LambdalabsError):
    """
        Raised when a requested instance-type name is not present in the
        Lambda Labs instance-types catalog.
    """


class LambdalabsQuotaExceededError(LambdalabsError):
    """
        Raised when a launch request would exceed the account's instance
        quota or available capacity.
    """


class LambdalabsInstanceFailedError(LambdalabsError):
    """
        Raised when an instance enters a terminal-failed state while the
        client is waiting for it to become active.
    """
