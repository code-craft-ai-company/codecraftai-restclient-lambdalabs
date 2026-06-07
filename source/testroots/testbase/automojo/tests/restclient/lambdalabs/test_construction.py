"""
    .. module:: test_construction
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Construction tests for :class:`LambdalabsClient` — valid
                   and invalid credential handling.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import pytest

from ccai.errors.exceptions import ConfigurationError

from ccai.credentials.basiccredential import BasicCredential

from ccai.restclient.lambdalabs.lambdalabsclient import LambdalabsClient

from ccai.tests.restclient.lambdalabs.testsupport import (
    make_client, make_credential
)


def test_construct_with_valid_credential():
    """
        A client constructs cleanly from a Lambda Labs API-key credential.
    """
    client = make_client()
    assert client.host == "cloud.lambdalabs.test"
    return


def test_construct_rejects_wrong_credential_type():
    """
        Construction raises ConfigurationError for a non-Lambda credential.
    """
    wrong = BasicCredential(identifier="wrong", categories=["basic"],
                            username="u", password="p")
    with pytest.raises(ConfigurationError):
        LambdalabsClient(credential=wrong)
    return


def test_construct_exposes_six_api_groups():
    """
        The client exposes the six documented api groups.
    """
    client = make_client()
    assert client.instance_types is not None
    assert client.images is not None
    assert client.ssh_keys is not None
    assert client.filesystems is not None
    assert client.instances is not None
    assert client.clusters is not None
    return


def test_credential_token_is_required():
    """
        A credential constructed without a token cannot exist; the
        credential class itself enforces the non-empty token.
    """
    with pytest.raises(ConfigurationError):
        from ccai.credentials.lambdalabsapikeycredential import (
            LambdalabsApiKeyCredential
        )
        LambdalabsApiKeyCredential(identifier="x", categories=["hpc-venue"],
                                   token="")
    # A valid credential still constructs a client.
    client = LambdalabsClient(credential=make_credential())
    assert client is not None
    return
