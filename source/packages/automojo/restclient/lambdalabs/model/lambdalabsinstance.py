"""
    .. module:: lambdalabsinstance
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsInstance`
                   hand-authored typed model for a Lambda Labs instance.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


# Lambda Labs instance lifecycle states observed on the public API.
STATUS_BOOTING = "booting"
STATUS_ACTIVE = "active"
STATUS_UNHEALTHY = "unhealthy"
STATUS_TERMINATING = "terminating"
STATUS_TERMINATED = "terminated"

TERMINAL_FAILED_STATES = frozenset({STATUS_UNHEALTHY})


class LambdalabsInstance:
    """
        Typed model describing a single Lambda Labs instance.

        Hand-authored from the published Lambda Labs REST documentation.
        The ``status`` field carries the lifecycle state; the IP and SSH
        host fields are only populated once the instance is ``active``.
    """

    def __init__(self, *, identifier: str, name: str, status: str,
                 region: str, instance_type_name: str,
                 ip: Optional[str] = None,
                 private_ip: Optional[str] = None,
                 hostname: Optional[str] = None,
                 ssh_key_names: Optional[List[str]] = None,
                 file_system_names: Optional[List[str]] = None,
                 jupyter_url: Optional[str] = None) -> None:
        """
            Initialize a :class:`LambdalabsInstance`.

            :param identifier: The instance identifier assigned by Lambda
                Labs.
            :param name: The instance name.
            :param status: The lifecycle state string.
            :param region: The region the instance lives in.
            :param instance_type_name: The instance-type slug.
            :param ip: The public IP, once assigned.
            :param private_ip: The private IP, once assigned.
            :param hostname: The SSH host name, once assigned.
            :param ssh_key_names: The SSH key names attached at launch.
            :param file_system_names: The file-system names attached at
                launch.
            :param jupyter_url: The Jupyter notebook URL, when available.

            :returns: ``None``.
        """
        self._identifier = identifier
        self._name = name
        self._status = status
        self._region = region
        self._instance_type_name = instance_type_name
        self._ip = ip
        self._private_ip = private_ip
        self._hostname = hostname
        if ssh_key_names is not None:
            self._ssh_key_names = list(ssh_key_names)
        else:
            self._ssh_key_names = []
        if file_system_names is not None:
            self._file_system_names = list(file_system_names)
        else:
            self._file_system_names = []
        self._jupyter_url = jupyter_url
        return

    @property
    def identifier(self) -> str:
        """
            The instance identifier.

            :returns: The identifier string.
        """
        return self._identifier

    @property
    def name(self) -> str:
        """
            The instance name.

            :returns: The name string.
        """
        return self._name

    @property
    def status(self) -> str:
        """
            The lifecycle state string.

            :returns: The status string.
        """
        return self._status

    @property
    def region(self) -> str:
        """
            The region the instance lives in.

            :returns: The region string.
        """
        return self._region

    @property
    def instance_type_name(self) -> str:
        """
            The instance-type slug.

            :returns: The instance-type slug string.
        """
        return self._instance_type_name

    @property
    def ip(self) -> Optional[str]:
        """
            The public IP, once assigned.

            :returns: The public IP string, or ``None``.
        """
        return self._ip

    @property
    def private_ip(self) -> Optional[str]:
        """
            The private IP, once assigned.

            :returns: The private IP string, or ``None``.
        """
        return self._private_ip

    @property
    def hostname(self) -> Optional[str]:
        """
            The SSH host name, once assigned.

            :returns: The SSH host name string, or ``None``.
        """
        return self._hostname

    @property
    def ssh_key_names(self) -> List[str]:
        """
            The SSH key names attached at launch.

            :returns: A defensive copy of the SSH key name list.
        """
        rtnval = list(self._ssh_key_names)
        return rtnval

    @property
    def file_system_names(self) -> List[str]:
        """
            The file-system names attached at launch.

            :returns: A defensive copy of the file-system name list.
        """
        rtnval = list(self._file_system_names)
        return rtnval

    @property
    def jupyter_url(self) -> Optional[str]:
        """
            The Jupyter notebook URL, when available.

            :returns: The Jupyter URL string, or ``None``.
        """
        return self._jupyter_url

    @property
    def is_active(self) -> bool:
        """
            Whether the instance has reached the ``active`` state.

            :returns: ``True`` when the instance is active.
        """
        rtnval = self._status == STATUS_ACTIVE
        return rtnval

    @property
    def is_terminal_failed(self) -> bool:
        """
            Whether the instance has entered a terminal-failed state.

            :returns: ``True`` when the instance has failed terminally.
        """
        rtnval = self._status in TERMINAL_FAILED_STATES
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`LambdalabsInstance` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this instance.
        """
        rtnval: Dict[str, Any] = {
            "id": self._identifier,
            "name": self._name,
            "status": self._status,
            "region": self._region,
            "instance_type": self._instance_type_name,
            "ip": self._ip,
            "private_ip": self._private_ip,
            "hostname": self._hostname,
            "ssh_key_names": list(self._ssh_key_names),
            "file_system_names": list(self._file_system_names),
            "jupyter_url": self._jupyter_url,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LambdalabsInstance":
        """
            Construct a :class:`LambdalabsInstance` from an API payload
            entry.

            :param data: The raw API payload entry.

            :returns: A populated :class:`LambdalabsInstance`.
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

        ssh_keys_payload = data.get("ssh_key_names", None)
        fs_payload = data.get("file_system_names", None)

        rtnval = cls(
            identifier=data.get("id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            region=region_name,
            instance_type_name=type_name,
            ip=data.get("ip", None),
            private_ip=data.get("private_ip", None),
            hostname=data.get("hostname", None),
            ssh_key_names=ssh_keys_payload,
            file_system_names=fs_payload,
            jupyter_url=data.get("jupyter_url", None),
        )
        return rtnval
