"""
    .. module:: lambdalabsclusterspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsClusterSpec`
                   request spec for creating Lambda Labs 1-click clusters.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class LambdalabsClusterSpec:
    """
        Request spec describing a Lambda Labs 1-click cluster creation call.

        Hand-authored from the published Lambda Labs REST documentation.
        A 1-click cluster provisions an InfiniBand-connected group of nodes
        of a single instance type in a single API call.
    """

    def __init__(self, *, name: str, region_name: str,
                 instance_type_name: str, node_count: int,
                 ssh_key_names: Optional[List[str]] = None,
                 file_system_names: Optional[List[str]] = None,
                 user_data: Optional[str] = None) -> None:
        """
            Initialize a :class:`LambdalabsClusterSpec`.

            :param name: The cluster name.
            :param region_name: The region to create the cluster in.
            :param instance_type_name: The instance-type slug for the nodes.
            :param node_count: Number of nodes in the cluster; must be > 0.
            :param ssh_key_names: SSH key names to attach to the nodes.
            :param file_system_names: File-system names to attach.
            :param user_data: Optional cloud-init / launch metadata payload.

            :returns: ``None``.
        """
        self._name = name
        self._region_name = region_name
        self._instance_type_name = instance_type_name
        self._node_count = node_count
        if ssh_key_names is not None:
            self._ssh_key_names = list(ssh_key_names)
        else:
            self._ssh_key_names = []
        if file_system_names is not None:
            self._file_system_names = list(file_system_names)
        else:
            self._file_system_names = []
        self._user_data = user_data
        return

    @property
    def name(self) -> str:
        """
            The cluster name.

            :returns: The cluster name string.
        """
        return self._name

    @property
    def region_name(self) -> str:
        """
            The region to create the cluster in.

            :returns: The region name string.
        """
        return self._region_name

    @property
    def instance_type_name(self) -> str:
        """
            The instance-type slug for the cluster nodes.

            :returns: The instance-type slug string.
        """
        return self._instance_type_name

    @property
    def node_count(self) -> int:
        """
            Number of nodes in the cluster.

            :returns: The node count.
        """
        return self._node_count

    @property
    def ssh_key_names(self) -> List[str]:
        """
            SSH key names to attach to the cluster nodes.

            :returns: A defensive copy of the SSH key name list.
        """
        rtnval = list(self._ssh_key_names)
        return rtnval

    @property
    def file_system_names(self) -> List[str]:
        """
            File-system names to attach to the cluster nodes.

            :returns: A defensive copy of the file-system name list.
        """
        rtnval = list(self._file_system_names)
        return rtnval

    @property
    def user_data(self) -> Optional[str]:
        """
            The optional cloud-init / launch metadata payload.

            :returns: The user-data string, or ``None``.
        """
        return self._user_data

    def to_dict(self) -> Dict[str, Any]:
        """
            Render this spec into the Lambda Labs cluster request body.

            :returns: A dictionary suitable for the cluster create POST body.
        """
        rtnval: Dict[str, Any] = {
            "name": self._name,
            "region_name": self._region_name,
            "instance_type_name": self._instance_type_name,
            "node_count": self._node_count,
            "ssh_key_names": list(self._ssh_key_names),
        }
        if len(self._file_system_names) > 0:
            rtnval["file_system_names"] = list(self._file_system_names)
        if self._user_data is not None:
            rtnval["user_data"] = self._user_data
        return rtnval
