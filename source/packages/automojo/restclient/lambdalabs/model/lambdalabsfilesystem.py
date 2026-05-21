"""
    .. module:: lambdalabsfilesystem
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsFilesystem`
                   hand-authored typed model for a Lambda Labs file system.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class LambdalabsFilesystem:
    """
        Typed model describing a Lambda Labs persistent (NFS) file system.

        Hand-authored from the published Lambda Labs REST documentation.
    """

    def __init__(self, *, identifier: str, name: str, region: str,
                 mount_point: Optional[str] = None,
                 is_in_use: bool = False,
                 bytes_used: Optional[int] = None) -> None:
        """
            Initialize a :class:`LambdalabsFilesystem`.

            :param identifier: The file-system identifier assigned by
                Lambda Labs.
            :param name: The file-system name.
            :param region: The region the file system lives in.
            :param mount_point: The mount point path on attached instances.
            :param is_in_use: Whether the file system is currently attached.
            :param bytes_used: Bytes currently used on the file system.

            :returns: ``None``.
        """
        self._identifier = identifier
        self._name = name
        self._region = region
        self._mount_point = mount_point
        self._is_in_use = is_in_use
        self._bytes_used = bytes_used
        return

    @property
    def identifier(self) -> str:
        """
            The file-system identifier.

            :returns: The identifier string.
        """
        return self._identifier

    @property
    def name(self) -> str:
        """
            The file-system name.

            :returns: The name string.
        """
        return self._name

    @property
    def region(self) -> str:
        """
            The region the file system lives in.

            :returns: The region string.
        """
        return self._region

    @property
    def mount_point(self) -> Optional[str]:
        """
            The mount point path on attached instances.

            :returns: The mount point string, or ``None``.
        """
        return self._mount_point

    @property
    def is_in_use(self) -> bool:
        """
            Whether the file system is currently attached to an instance.

            :returns: ``True`` when in use.
        """
        return self._is_in_use

    @property
    def bytes_used(self) -> Optional[int]:
        """
            Bytes currently used on the file system.

            :returns: The bytes-used count, or ``None``.
        """
        return self._bytes_used

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`LambdalabsFilesystem` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this file system.
        """
        rtnval: Dict[str, Any] = {
            "id": self._identifier,
            "name": self._name,
            "region": self._region,
            "mount_point": self._mount_point,
            "is_in_use": self._is_in_use,
            "bytes_used": self._bytes_used,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LambdalabsFilesystem":
        """
            Construct a :class:`LambdalabsFilesystem` from an API payload
            entry.

            :param data: The raw API payload entry.

            :returns: A populated :class:`LambdalabsFilesystem`.
        """
        region_payload = data.get("region", None)
        region_name = ""
        if region_payload is not None:
            if isinstance(region_payload, dict):
                region_name = region_payload.get("name", "")
            else:
                region_name = region_payload

        rtnval = cls(
            identifier=data.get("id", ""),
            name=data.get("name", ""),
            region=region_name,
            mount_point=data.get("mount_point", None),
            is_in_use=data.get("is_in_use", False),
            bytes_used=data.get("bytes_used", None),
        )
        return rtnval
