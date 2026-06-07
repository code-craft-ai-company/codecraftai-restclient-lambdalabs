"""
    .. module:: lambdalabscluster
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsCluster`
                   hand-authored typed model for a Lambda Labs 1-click
                   cluster.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class LambdalabsCluster:
    """
        Typed model describing a Lambda Labs 1-click cluster — a group of
        InfiniBand-connected instances provisioned in a single API call.

        Hand-authored from the published Lambda Labs REST documentation.
    """

    def __init__(self, *, identifier: str, name: str, status: str,
                 region: str, instance_type_name: str,
                 instance_ids: Optional[List[str]] = None,
                 interconnect_status: Optional[str] = None) -> None:
        """
            Initialize a :class:`LambdalabsCluster`.

            :param identifier: The cluster identifier assigned by Lambda
                Labs.
            :param name: The cluster name.
            :param status: The cluster lifecycle state string.
            :param region: The region the cluster lives in.
            :param instance_type_name: The instance-type slug for the
                member nodes.
            :param instance_ids: The member instance identifiers.
            :param interconnect_status: The InfiniBand interconnect status.

            :returns: ``None``.
        """
        self._identifier = identifier
        self._name = name
        self._status = status
        self._region = region
        self._instance_type_name = instance_type_name
        if instance_ids is not None:
            self._instance_ids = list(instance_ids)
        else:
            self._instance_ids = []
        self._interconnect_status = interconnect_status
        return

    @property
    def identifier(self) -> str:
        """
            The cluster identifier.

            :returns: The identifier string.
        """
        return self._identifier

    @property
    def name(self) -> str:
        """
            The cluster name.

            :returns: The name string.
        """
        return self._name

    @property
    def status(self) -> str:
        """
            The cluster lifecycle state.

            :returns: The status string.
        """
        return self._status

    @property
    def region(self) -> str:
        """
            The region the cluster lives in.

            :returns: The region string.
        """
        return self._region

    @property
    def instance_type_name(self) -> str:
        """
            The instance-type slug for the member nodes.

            :returns: The instance-type slug string.
        """
        return self._instance_type_name

    @property
    def instance_ids(self) -> List[str]:
        """
            The member instance identifiers.

            :returns: A defensive copy of the instance id list.
        """
        rtnval = list(self._instance_ids)
        return rtnval

    @property
    def interconnect_status(self) -> Optional[str]:
        """
            The InfiniBand interconnect status.

            :returns: The interconnect status string, or ``None``.
        """
        return self._interconnect_status

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`LambdalabsCluster` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this cluster.
        """
        rtnval: Dict[str, Any] = {
            "id": self._identifier,
            "name": self._name,
            "status": self._status,
            "region": self._region,
            "instance_type": self._instance_type_name,
            "instance_ids": list(self._instance_ids),
            "interconnect_status": self._interconnect_status,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LambdalabsCluster":
        """
            Construct a :class:`LambdalabsCluster` from an API payload
            entry.

            :param data: The raw API payload entry.

            :returns: A populated :class:`LambdalabsCluster`.
        """
        region_payload = data.get("region", None)
        region_name = ""
        if region_payload is not None:
            if isinstance(region_payload, dict):
                region_name = region_payload.get("name", "")
            else:
                region_name = region_payload

        type_payload = data.get("instance_type", None)
        type_name = ""
        if type_payload is not None:
            if isinstance(type_payload, dict):
                type_name = type_payload.get("name", "")
            else:
                type_name = type_payload

        rtnval = cls(
            identifier=data.get("id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            region=region_name,
            instance_type_name=type_name,
            instance_ids=data.get("instance_ids", None),
            interconnect_status=data.get("interconnect_status", None),
        )
        return rtnval
