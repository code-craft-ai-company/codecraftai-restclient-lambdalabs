"""
    .. module:: test_apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for each Lambda Labs api-group method — URL
                   composition, body shape, header presence, and
                   idempotent register/create behaviour — with all HTTP
                   traffic mocked via ``requests-mock``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import json

import pytest
import requests_mock as rm_module

from automojo.restclient.lambdalabs.model.lambdalabsinstance import (
    LambdalabsInstance
)
from automojo.restclient.lambdalabs.model.lambdalabssshkey import LambdalabsSshKey
from automojo.restclient.lambdalabs.specs.lambdalabsclusterspec import (
    LambdalabsClusterSpec
)
from automojo.restclient.lambdalabs.specs.lambdalabslaunchspec import (
    LambdalabsLaunchSpec
)

from automojo.tests.restclient.lambdalabs.testsupport import (
    API, data_envelope, make_client
)


def test_list_instance_types_url_and_parsing():
    """
        ``list_instance_types`` composes the instance-types URL and parses
        records carrying GPU model, count, and region capacity.
    """
    client = make_client()
    payload = {
        "gpu_1x_h100_pcie": {
            "instance_type": {
                "name": "gpu_1x_h100_pcie",
                "description": "1x H100 (PCIe)",
                "gpu_description": "H100 PCIe",
                "price_cents_per_hour": 219,
                "specs": {"vcpus": 26, "memory_gib": 200,
                          "storage_gib": 1024, "gpus": 1},
            },
            "regions_with_capacity_available": [
                {"name": "us-east-1", "description": "Virginia"},
            ],
        },
    }
    with rm_module.Mocker() as mock:
        mock.get("{}/instance-types".format(API),
                 json=data_envelope(payload=payload))
        types = client.list_instance_types()
        assert mock.last_request.path == "/api/v1/instance-types"

    assert len(types) == 1
    assert types[0].name == "gpu_1x_h100_pcie"
    assert types[0].gpu_count == 1
    assert types[0].regions_with_capacity == ["us-east-1"]
    return


def test_list_images_parsing():
    """
        ``list_images`` parses image records.
    """
    client = make_client()
    payload = [
        {"id": "img-1", "name": "Ubuntu 22.04", "family": "ubuntu",
         "version": "22.04", "architecture": "x86_64"},
    ]
    with rm_module.Mocker() as mock:
        mock.get("{}/images".format(API), json=data_envelope(payload=payload))
        images = client.list_images()

    assert len(images) == 1
    assert images[0].family == "ubuntu"
    return


def test_register_ssh_key_is_idempotent_when_name_exists():
    """
        ``register_ssh_key`` returns the existing key when the name is
        already registered and issues no POST.
    """
    client = make_client()
    existing = [{"id": "k1", "name": "lab-key",
                 "public_key": "ssh-ed25519 AAAA lab"}]
    with rm_module.Mocker() as mock:
        mock.get("{}/ssh-keys".format(API),
                 json=data_envelope(payload=existing))
        post_marker = mock.post("{}/ssh-keys".format(API),
                                json=data_envelope(payload={}))
        key = client.register_ssh_key(name="lab-key",
                                      public_key="ssh-ed25519 AAAA other")

    assert isinstance(key, LambdalabsSshKey) is True
    assert key.identifier == "k1"
    assert post_marker.called is False
    return


def test_register_ssh_key_posts_when_absent():
    """
        ``register_ssh_key`` POSTs the key when no key of that name exists.
    """
    client = make_client()
    created = {"id": "k2", "name": "new-key",
               "public_key": "ssh-ed25519 AAAA new"}
    with rm_module.Mocker() as mock:
        mock.get("{}/ssh-keys".format(API), json=data_envelope(payload=[]))
        mock.post("{}/ssh-keys".format(API),
                  json=data_envelope(payload=created))
        key = client.register_ssh_key(name="new-key",
                                      public_key="ssh-ed25519 AAAA new")
        sent = json.loads(mock.last_request.body)
        assert sent == {"name": "new-key",
                        "public_key": "ssh-ed25519 AAAA new"}

    assert key.identifier == "k2"
    return


def test_delete_ssh_key_treats_404_as_success():
    """
        ``delete_ssh_key`` treats a 404 as already-removed.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.delete("{}/ssh-keys/gone".format(API), status_code=404)
        client.delete_ssh_key(key_id="gone")
        assert mock.last_request.method == "DELETE"
    return


def test_create_filesystem_is_idempotent_when_name_and_region_match():
    """
        ``create_filesystem`` returns the existing file system when the
        name and region both match and issues no POST.
    """
    client = make_client()
    existing = [{"id": "fs1", "name": "shared",
                 "region": {"name": "us-east-1"}}]
    with rm_module.Mocker() as mock:
        mock.get("{}/file-systems".format(API),
                 json=data_envelope(payload=existing))
        post_marker = mock.post("{}/file-systems".format(API),
                                json=data_envelope(payload={}))
        fs = client.create_filesystem(name="shared", region="us-east-1")

    assert fs.identifier == "fs1"
    assert post_marker.called is False
    return


def test_launch_instances_posts_spec_body():
    """
        ``launch_instances`` POSTs the rendered launch-spec body.
    """
    client = make_client()
    launched = [{"id": "i1", "name": "node-a", "status": "booting",
                 "region": {"name": "us-east-1"},
                 "instance_type": {"name": "gpu_1x_h100_pcie"}}]
    spec = LambdalabsLaunchSpec(region_name="us-east-1",
                                instance_type_name="gpu_1x_h100_pcie",
                                ssh_key_names=["lab-key"], name="node-a",
                                quantity=1, user_data="#cloud-config\n")
    with rm_module.Mocker() as mock:
        mock.post("{}/instance-operations/launch".format(API),
                  json=data_envelope(payload=launched))
        instances = client.launch_instances(spec=spec)
        sent = json.loads(mock.last_request.body)
        assert sent["region_name"] == "us-east-1"
        assert sent["instance_type_name"] == "gpu_1x_h100_pcie"
        assert sent["ssh_key_names"] == ["lab-key"]
        assert sent["user_data"] == "#cloud-config\n"

    assert len(instances) == 1
    assert isinstance(instances[0], LambdalabsInstance) is True
    assert instances[0].identifier == "i1"
    return


def test_get_instance_url_and_parsing():
    """
        ``get_instance`` composes the per-instance URL and parses IP fields.
    """
    client = make_client()
    payload = {"id": "i1", "name": "node-a", "status": "active",
               "region": {"name": "us-east-1"},
               "instance_type": {"name": "gpu_1x_h100_pcie"},
               "ip": "203.0.113.5", "private_ip": "10.0.0.5"}
    with rm_module.Mocker() as mock:
        mock.get("{}/instances/i1".format(API),
                 json=data_envelope(payload=payload))
        instance = client.get_instance(instance_id="i1")
        assert mock.last_request.path == "/api/v1/instances/i1"

    assert instance.ip == "203.0.113.5"
    assert instance.is_active is True
    return


def test_terminate_instances_reports_per_id_status():
    """
        ``terminate_instances`` reports per-id status, classifying ids that
        did not transition as already-terminated.
    """
    client = make_client()
    terminated = {"terminated_instances": [
        {"id": "i1", "name": "node-a", "status": "terminating",
         "region": {"name": "us-east-1"},
         "instance_type": {"name": "gpu_1x_h100_pcie"}},
    ]}
    with rm_module.Mocker() as mock:
        mock.post("{}/instance-operations/terminate".format(API),
                  json=data_envelope(payload=terminated))
        result = client.terminate_instances(instance_ids=["i1", "i2"])

    assert result.status_for(instance_id="i1") == "terminated"
    assert result.status_for(instance_id="i2") == "already-terminated"
    return


def test_create_cluster_posts_spec_body():
    """
        ``create_cluster`` POSTs the rendered cluster-spec body.
    """
    client = make_client()
    created = {"id": "c1", "name": "train-cluster", "status": "creating",
               "region": {"name": "us-east-1"},
               "instance_type": {"name": "gpu_8x_h100_sxm5"},
               "instance_ids": ["i1", "i2"]}
    spec = LambdalabsClusterSpec(name="train-cluster", region_name="us-east-1",
                                 instance_type_name="gpu_8x_h100_sxm5",
                                 node_count=2, ssh_key_names=["lab-key"])
    with rm_module.Mocker() as mock:
        mock.post("{}/1-click-clusters".format(API),
                  json=data_envelope(payload=created))
        cluster = client.create_cluster(spec=spec)
        sent = json.loads(mock.last_request.body)
        assert sent["node_count"] == 2

    assert cluster.identifier == "c1"
    assert cluster.instance_ids == ["i1", "i2"]
    return


def test_delete_cluster_treats_404_as_success():
    """
        ``delete_cluster`` treats a 404 as already-removed.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.delete("{}/1-click-clusters/gone".format(API), status_code=404)
        client.delete_cluster(cluster_id="gone")
    return


def test_authorization_header_present():
    """
        Every request carries the Bearer ``Authorization`` header.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/instances".format(API), json=data_envelope(payload=[]))
        client.list_instances()
        auth = mock.last_request.headers.get("Authorization")
        assert auth == "Bearer secret_lambdalabs_test_0001"
    return
