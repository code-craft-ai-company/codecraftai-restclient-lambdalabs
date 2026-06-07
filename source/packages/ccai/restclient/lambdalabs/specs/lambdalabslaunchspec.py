"""
    .. module:: lambdalabslaunchspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsLaunchSpec`
                   request spec for launching Lambda Labs instances.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class LambdalabsLaunchSpec:
    """
        Request spec describing a Lambda Labs ``instance-operations/launch``
        call.

        Hand-authored from the published Lambda Labs REST documentation.
        ``user_data`` carries the cloud-init payload used to bootstrap a
        VPN join when the provisioner attaches a ``VPNJoinSpec``.
    """

    def __init__(self, *, region_name: str, instance_type_name: str,
                 ssh_key_names: Optional[List[str]] = None,
                 file_system_names: Optional[List[str]] = None,
                 name: Optional[str] = None, quantity: int = 1,
                 user_data: Optional[str] = None) -> None:
        """
            Initialize a :class:`LambdalabsLaunchSpec`.

            :param region_name: The region to launch in.
            :param instance_type_name: The instance-type slug to launch.
            :param ssh_key_names: SSH key names to attach to the instance.
            :param file_system_names: File-system names to attach.
            :param name: Optional instance name.
            :param quantity: Number of instances to launch; must be > 0.
            :param user_data: Optional cloud-init / launch metadata payload.

            :returns: ``None``.
        """
        self._region_name = region_name
        self._instance_type_name = instance_type_name
        if ssh_key_names is not None:
            self._ssh_key_names = list(ssh_key_names)
        else:
            self._ssh_key_names = []
        if file_system_names is not None:
            self._file_system_names = list(file_system_names)
        else:
            self._file_system_names = []
        self._name = name
        self._quantity = quantity
        self._user_data = user_data
        return

    @property
    def region_name(self) -> str:
        """
            The region to launch in.

            :returns: The region name string.
        """
        return self._region_name

    @property
    def instance_type_name(self) -> str:
        """
            The instance-type slug to launch.

            :returns: The instance-type slug string.
        """
        return self._instance_type_name

    @property
    def ssh_key_names(self) -> List[str]:
        """
            SSH key names to attach to the instance.

            :returns: A defensive copy of the SSH key name list.
        """
        rtnval = list(self._ssh_key_names)
        return rtnval

    @property
    def file_system_names(self) -> List[str]:
        """
            File-system names to attach to the instance.

            :returns: A defensive copy of the file-system name list.
        """
        rtnval = list(self._file_system_names)
        return rtnval

    @property
    def name(self) -> Optional[str]:
        """
            The optional instance name.

            :returns: The name string, or ``None``.
        """
        return self._name

    @property
    def quantity(self) -> int:
        """
            Number of instances to launch.

            :returns: The launch quantity.
        """
        return self._quantity

    @property
    def user_data(self) -> Optional[str]:
        """
            The optional cloud-init / launch metadata payload.

            :returns: The user-data string, or ``None``.
        """
        return self._user_data

    def to_dict(self) -> Dict[str, Any]:
        """
            Render this spec into the Lambda Labs launch request body.

            :returns: A dictionary suitable for the launch POST body.
        """
        rtnval: Dict[str, Any] = {
            "region_name": self._region_name,
            "instance_type_name": self._instance_type_name,
            "ssh_key_names": list(self._ssh_key_names),
            "quantity": self._quantity,
        }
        if len(self._file_system_names) > 0:
            rtnval["file_system_names"] = list(self._file_system_names)
        if self._name is not None:
            rtnval["name"] = self._name
        if self._user_data is not None:
            rtnval["user_data"] = self._user_data
        return rtnval
