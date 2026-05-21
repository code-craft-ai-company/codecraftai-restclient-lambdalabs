"""
    .. module:: lambdalabsinstancetype
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsInstanceType`
                   hand-authored typed model for a Lambda Labs instance type.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class LambdalabsInstanceType:
    """
        Typed model describing a single Lambda Labs instance type and its
        per-region capacity.

        Lambda Labs publishes no OpenAPI document, so this class is
        hand-authored from the published REST documentation.  The
        ``regions_with_capacity`` list carries the region names where the
        instance type is currently launchable.
    """

    def __init__(self, *, name: str, description: str, gpu_description: str,
                 price_cents_per_hour: int, vcpus: int, memory_gib: int,
                 storage_gib: int, gpu_count: int,
                 regions_with_capacity: Optional[List[str]] = None) -> None:
        """
            Initialize a :class:`LambdalabsInstanceType`.

            :param name: The instance-type slug (e.g. ``gpu_1x_h100_pcie``).
            :param description: Human-readable description.
            :param gpu_description: Human-readable GPU model description.
            :param price_cents_per_hour: Hourly price in US cents.
            :param vcpus: Number of virtual CPUs.
            :param memory_gib: System memory in gibibytes.
            :param storage_gib: Local storage in gibibytes.
            :param gpu_count: Number of GPUs in the instance type.
            :param regions_with_capacity: Region names that currently have
                capacity for this instance type.

            :returns: ``None``.
        """
        self._name = name
        self._description = description
        self._gpu_description = gpu_description
        self._price_cents_per_hour = price_cents_per_hour
        self._vcpus = vcpus
        self._memory_gib = memory_gib
        self._storage_gib = storage_gib
        self._gpu_count = gpu_count
        if regions_with_capacity is not None:
            self._regions_with_capacity = list(regions_with_capacity)
        else:
            self._regions_with_capacity = []
        return

    @property
    def name(self) -> str:
        """
            The instance-type slug.

            :returns: The instance-type slug string.
        """
        return self._name

    @property
    def description(self) -> str:
        """
            Human-readable description of the instance type.

            :returns: The description string.
        """
        return self._description

    @property
    def gpu_description(self) -> str:
        """
            Human-readable GPU model description.

            :returns: The GPU description string.
        """
        return self._gpu_description

    @property
    def price_cents_per_hour(self) -> int:
        """
            Hourly price in US cents.

            :returns: The hourly price in cents.
        """
        return self._price_cents_per_hour

    @property
    def vcpus(self) -> int:
        """
            Number of virtual CPUs.

            :returns: The vCPU count.
        """
        return self._vcpus

    @property
    def memory_gib(self) -> int:
        """
            System memory in gibibytes.

            :returns: The system memory in GiB.
        """
        return self._memory_gib

    @property
    def storage_gib(self) -> int:
        """
            Local storage in gibibytes.

            :returns: The local storage in GiB.
        """
        return self._storage_gib

    @property
    def gpu_count(self) -> int:
        """
            Number of GPUs in the instance type.

            :returns: The GPU count.
        """
        return self._gpu_count

    @property
    def regions_with_capacity(self) -> List[str]:
        """
            Region names that currently have capacity for this type.

            :returns: A defensive copy of the capacity region list.
        """
        rtnval = list(self._regions_with_capacity)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`LambdalabsInstanceType` to a canonical
            API payload.

            The Lambda Labs ``instance-types`` payload nests the type
            description under an ``instance_type`` key (with a ``specs``
            sub-object) and the capacity list under a sibling
            ``regions_with_capacity_available`` key.  This method emits that
            same nested shape so ``from_dict(to_dict(x))`` reconstructs an
            equal record.

            :returns: A nested dictionary payload describing this type.
        """
        specs: Dict[str, Any] = {
            "vcpus": self._vcpus,
            "memory_gib": self._memory_gib,
            "storage_gib": self._storage_gib,
            "gpus": self._gpu_count,
        }
        instance_type: Dict[str, Any] = {
            "name": self._name,
            "description": self._description,
            "gpu_description": self._gpu_description,
            "price_cents_per_hour": self._price_cents_per_hour,
            "specs": specs,
        }
        regions: List[Dict[str, str]] = []
        for region_name in self._regions_with_capacity:
            regions.append({"name": region_name})

        rtnval: Dict[str, Any] = {
            "instance_type": instance_type,
            "regions_with_capacity_available": regions,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LambdalabsInstanceType":
        """
            Construct a :class:`LambdalabsInstanceType` from a Lambda Labs
            ``instance-types`` API payload entry.

            The Lambda Labs payload nests the instance type description in
            an ``instance_type`` key and the capacity list in a sibling
            ``regions_with_capacity_available`` key.

            :param data: The raw API payload entry.

            :returns: A populated :class:`LambdalabsInstanceType`.
        """
        type_payload = data.get("instance_type", None)
        if type_payload is None:
            type_payload = data

        specs = type_payload.get("specs", None)
        if specs is None:
            specs = {}

        regions_payload = data.get("regions_with_capacity_available", None)
        regions: List[str] = []
        if regions_payload is not None:
            for entry in regions_payload:
                if isinstance(entry, dict):
                    region_name = entry.get("name", None)
                    if region_name is not None:
                        regions.append(region_name)
                else:
                    regions.append(entry)

        rtnval = cls(
            name=type_payload.get("name", ""),
            description=type_payload.get("description", ""),
            gpu_description=type_payload.get("gpu_description", ""),
            price_cents_per_hour=type_payload.get("price_cents_per_hour", 0),
            vcpus=specs.get("vcpus", 0),
            memory_gib=specs.get("memory_gib", 0),
            storage_gib=specs.get("storage_gib", 0),
            gpu_count=specs.get("gpus", 0),
            regions_with_capacity=regions,
        )
        return rtnval
