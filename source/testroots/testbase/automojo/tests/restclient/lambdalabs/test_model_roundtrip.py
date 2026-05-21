"""
    .. module:: test_model_roundtrip
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Round-trip tests verifying that every hand-authored Lambda
                   Labs model record is reconstructed exactly by
                   ``from_dict(to_dict(x))``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.restclient.lambdalabs.model.lambdalabscluster import (
    LambdalabsCluster
)
from automojo.restclient.lambdalabs.model.lambdalabsfilesystem import (
    LambdalabsFilesystem
)
from automojo.restclient.lambdalabs.model.lambdalabsimage import (
    LambdalabsImage
)
from automojo.restclient.lambdalabs.model.lambdalabsinstance import (
    LambdalabsInstance
)
from automojo.restclient.lambdalabs.model.lambdalabsinstancetype import (
    LambdalabsInstanceType
)
from automojo.restclient.lambdalabs.model.lambdalabssshkey import (
    LambdalabsSshKey
)


def test_cluster_roundtrip() -> None:
    """
        A populated :class:`LambdalabsCluster` survives the round trip.
    """
    original = LambdalabsCluster(identifier="cl-1", name="train",
                                 status="active", region="us-east-1",
                                 instance_type_name="gpu_8x_h100",
                                 instance_ids=["i-1", "i-2"],
                                 interconnect_status="ready")
    rebuilt = LambdalabsCluster.from_dict(original.to_dict())

    assert rebuilt.identifier == original.identifier
    assert rebuilt.name == original.name
    assert rebuilt.status == original.status
    assert rebuilt.region == original.region
    assert rebuilt.instance_type_name == original.instance_type_name
    assert rebuilt.instance_ids == original.instance_ids
    assert rebuilt.interconnect_status == original.interconnect_status
    return


def test_filesystem_roundtrip() -> None:
    """
        A populated :class:`LambdalabsFilesystem` survives the round trip.
    """
    original = LambdalabsFilesystem(identifier="fs-1", name="shared",
                                    region="us-east-1",
                                    mount_point="/home/ubuntu/shared",
                                    is_in_use=True, bytes_used=4096)
    rebuilt = LambdalabsFilesystem.from_dict(original.to_dict())

    assert rebuilt.identifier == original.identifier
    assert rebuilt.name == original.name
    assert rebuilt.region == original.region
    assert rebuilt.mount_point == original.mount_point
    assert rebuilt.is_in_use == original.is_in_use
    assert rebuilt.bytes_used == original.bytes_used
    return


def test_image_roundtrip() -> None:
    """
        A populated :class:`LambdalabsImage` survives the round trip.
    """
    original = LambdalabsImage(identifier="img-1", name="ubuntu-22.04",
                               family="ubuntu", version="22.04",
                               architecture="x86_64", region="us-east-1")
    rebuilt = LambdalabsImage.from_dict(original.to_dict())

    assert rebuilt.identifier == original.identifier
    assert rebuilt.name == original.name
    assert rebuilt.family == original.family
    assert rebuilt.version == original.version
    assert rebuilt.architecture == original.architecture
    assert rebuilt.region == original.region
    return


def test_instance_roundtrip() -> None:
    """
        A populated :class:`LambdalabsInstance` survives the round trip.
    """
    original = LambdalabsInstance(identifier="i-1", name="node",
                                  status="active", region="us-east-1",
                                  instance_type_name="gpu_1x_h100",
                                  ip="1.2.3.4", private_ip="10.0.0.4",
                                  hostname="node.example.com",
                                  ssh_key_names=["key-a"],
                                  file_system_names=["fs-1"],
                                  jupyter_url="https://jupyter.example.com")
    rebuilt = LambdalabsInstance.from_dict(original.to_dict())

    assert rebuilt.identifier == original.identifier
    assert rebuilt.name == original.name
    assert rebuilt.status == original.status
    assert rebuilt.region == original.region
    assert rebuilt.instance_type_name == original.instance_type_name
    assert rebuilt.ip == original.ip
    assert rebuilt.private_ip == original.private_ip
    assert rebuilt.hostname == original.hostname
    assert rebuilt.ssh_key_names == original.ssh_key_names
    assert rebuilt.file_system_names == original.file_system_names
    assert rebuilt.jupyter_url == original.jupyter_url
    return


def test_instance_type_roundtrip() -> None:
    """
        A populated :class:`LambdalabsInstanceType` survives the round trip.
    """
    original = LambdalabsInstanceType(name="gpu_8x_h100",
                                      description="8x H100 node",
                                      gpu_description="NVIDIA H100",
                                      price_cents_per_hour=2999,
                                      vcpus=208, memory_gib=1800,
                                      storage_gib=24000, gpu_count=8,
                                      regions_with_capacity=["us-east-1",
                                                             "us-west-2"])
    rebuilt = LambdalabsInstanceType.from_dict(original.to_dict())

    assert rebuilt.name == original.name
    assert rebuilt.description == original.description
    assert rebuilt.gpu_description == original.gpu_description
    assert rebuilt.price_cents_per_hour == original.price_cents_per_hour
    assert rebuilt.vcpus == original.vcpus
    assert rebuilt.memory_gib == original.memory_gib
    assert rebuilt.storage_gib == original.storage_gib
    assert rebuilt.gpu_count == original.gpu_count
    assert rebuilt.regions_with_capacity == original.regions_with_capacity
    return


def test_ssh_key_roundtrip() -> None:
    """
        A populated :class:`LambdalabsSshKey` survives the round trip.
    """
    original = LambdalabsSshKey(identifier="key-1", name="laptop",
                                public_key="ssh-ed25519 AAAA...",
                                private_key="-----BEGIN KEY-----")
    rebuilt = LambdalabsSshKey.from_dict(original.to_dict())

    assert rebuilt.identifier == original.identifier
    assert rebuilt.name == original.name
    assert rebuilt.public_key == original.public_key
    assert rebuilt.private_key == original.private_key
    return
