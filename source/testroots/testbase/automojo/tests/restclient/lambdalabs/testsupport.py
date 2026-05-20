"""
    .. module:: testsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Shared construction helpers for the Lambda Labs interop
                   client test suite.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.credentials.lambdalabsapikeycredential import (
    LambdalabsApiKeyCredential
)

from automojo.restclient.lambdalabs.lambdalabsclient import LambdalabsClient


TEST_HOST = "cloud.lambdalabs.test"
TEST_TOKEN = "secret_lambdalabs_test_0001"

BASE = "https://{}".format(TEST_HOST)
API = "{}/api/v1".format(BASE)


def make_credential() -> LambdalabsApiKeyCredential:
    """
        Build a :class:`LambdalabsApiKeyCredential` for tests.

        :returns: A populated API-key credential.
    """
    rtnval = LambdalabsApiKeyCredential(identifier="ll-test-key",
                                        categories=["hpc-venue"],
                                        token=TEST_TOKEN)
    return rtnval


def make_client() -> LambdalabsClient:
    """
        Build a :class:`LambdalabsClient` against the test host.

        :returns: A constructed client.
    """
    rtnval = LambdalabsClient(credential=make_credential(), host=TEST_HOST)
    return rtnval


def data_envelope(*, payload: object) -> dict:
    """
        Wrap a payload in the Lambda Labs ``{"data": ...}`` envelope.

        :param payload: The payload to wrap.

        :returns: The wrapped envelope dict.
    """
    rtnval = {"data": payload}
    return rtnval


def error_envelope(*, code: str, message: str) -> dict:
    """
        Build a Lambda Labs ``{"error": {...}}`` error envelope.

        :param code: The Lambda Labs error code.
        :param message: The error message.

        :returns: The error envelope dict.
    """
    rtnval = {"error": {"code": code, "message": message}}
    return rtnval
