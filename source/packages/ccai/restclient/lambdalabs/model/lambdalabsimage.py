"""
    .. module:: lambdalabsimage
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsImage`
                   hand-authored typed model for a Lambda Labs OS image.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional


class LambdalabsImage:
    """
        Typed model describing a Lambda Labs operating-system image.

        Hand-authored from the published Lambda Labs REST documentation,
        which has no OpenAPI document.
    """

    def __init__(self, *, identifier: str, name: str, family: str,
                 version: str, architecture: str,
                 region: Optional[str] = None) -> None:
        """
            Initialize a :class:`LambdalabsImage`.

            :param identifier: The image identifier assigned by Lambda Labs.
            :param name: The image name.
            :param family: The OS family (e.g. ``ubuntu``).
            :param version: The OS version string.
            :param architecture: The CPU architecture (e.g. ``x86_64``).
            :param region: Optional region the image is published in.

            :returns: ``None``.
        """
        self._identifier = identifier
        self._name = name
        self._family = family
        self._version = version
        self._architecture = architecture
        self._region = region
        return

    @property
    def identifier(self) -> str:
        """
            The image identifier.

            :returns: The image identifier string.
        """
        return self._identifier

    @property
    def name(self) -> str:
        """
            The image name.

            :returns: The image name string.
        """
        return self._name

    @property
    def family(self) -> str:
        """
            The OS family.

            :returns: The OS family string.
        """
        return self._family

    @property
    def version(self) -> str:
        """
            The OS version.

            :returns: The OS version string.
        """
        return self._version

    @property
    def architecture(self) -> str:
        """
            The CPU architecture.

            :returns: The architecture string.
        """
        return self._architecture

    @property
    def region(self) -> Optional[str]:
        """
            The region the image is published in, if known.

            :returns: The region string, or ``None``.
        """
        return self._region

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`LambdalabsImage` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this image.
        """
        rtnval: Dict[str, Any] = {
            "id": self._identifier,
            "name": self._name,
            "family": self._family,
            "version": self._version,
            "architecture": self._architecture,
            "region": self._region,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LambdalabsImage":
        """
            Construct a :class:`LambdalabsImage` from an API payload entry.

            :param data: The raw API payload entry.

            :returns: A populated :class:`LambdalabsImage`.
        """
        region_payload = data.get("region", None)
        region_name: Optional[str] = None
        if region_payload is not None:
            if isinstance(region_payload, dict):
                region_name = region_payload.get("name", None)
            else:
                region_name = region_payload

        rtnval = cls(
            identifier=data.get("id", ""),
            name=data.get("name", ""),
            family=data.get("family", ""),
            version=data.get("version", ""),
            architecture=data.get("architecture", ""),
            region=region_name,
        )
        return rtnval
