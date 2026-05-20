"""
    .. module:: test_errors
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: HTTP-error reclassification tests for the Lambda Labs
                   interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest
import requests_mock as rm_module

from automojo.interop.lambdalabs.exceptions.lambdalabserrors import (
    LambdalabsAuthenticationError, LambdalabsError,
    LambdalabsInstanceTypeNotFoundError, LambdalabsQuotaExceededError
)
from automojo.interop.lambdalabs.specs.lambdalabslaunchspec import (
    LambdalabsLaunchSpec
)

from automojo.tests.interop.lambdalabs.testsupport import (
    API, data_envelope, error_envelope, make_client
)


def test_http_401_reclassifies_to_authentication_error():
    """
        An HTTP 401 reclassifies into LambdalabsAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/instances".format(API), status_code=401,
                 json=error_envelope(code="global/invalid-api-key",
                                     message="bad key"))
        with pytest.raises(LambdalabsAuthenticationError):
            client.list_instances()
    return


def test_http_403_reclassifies_to_authentication_error():
    """
        An HTTP 403 reclassifies into LambdalabsAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/instances".format(API), status_code=403,
                 json=error_envelope(code="global/forbidden",
                                     message="forbidden"))
        with pytest.raises(LambdalabsAuthenticationError):
            client.list_instances()
    return


def test_quota_error_reclassifies_to_quota_exceeded():
    """
        A launch carrying a quota-exceeded error code reclassifies into
        LambdalabsQuotaExceededError.
    """
    client = make_client()
    spec = LambdalabsLaunchSpec(region_name="us-east-1",
                                instance_type_name="gpu_1x_h100_pcie")
    with rm_module.Mocker() as mock:
        mock.post("{}/instance-operations/launch".format(API),
                  status_code=400,
                  json=error_envelope(code="global/quota-exceeded",
                                      message="over quota"))
        with pytest.raises(LambdalabsQuotaExceededError):
            client.launch_instances(spec=spec)
    return


def test_insufficient_capacity_reclassifies_to_quota_exceeded():
    """
        A launch failing for insufficient capacity reclassifies into
        LambdalabsQuotaExceededError.
    """
    client = make_client()
    spec = LambdalabsLaunchSpec(region_name="us-east-1",
                                instance_type_name="gpu_1x_h100_pcie")
    with rm_module.Mocker() as mock:
        mock.post("{}/instance-operations/launch".format(API),
                  status_code=400,
                  json=error_envelope(
                      code="instance-operations/launch/insufficient-capacity",
                      message="no capacity"))
        with pytest.raises(LambdalabsQuotaExceededError):
            client.launch_instances(spec=spec)
    return


def test_generic_500_reclassifies_to_lambdalabs_error():
    """
        An unclassified HTTP 500 reclassifies into the base LambdalabsError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/instances".format(API), status_code=500, text="boom")
        with pytest.raises(LambdalabsError):
            client.list_instances()
    return


def test_unknown_instance_type_raises_not_found():
    """
        ``get_instance_type`` raises LambdalabsInstanceTypeNotFoundError
        when the name is absent from the catalog.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/instance-types".format(API),
                 json=data_envelope(payload={}))
        with pytest.raises(LambdalabsInstanceTypeNotFoundError):
            client.get_instance_type(name="gpu_404x_unknown")
    return
