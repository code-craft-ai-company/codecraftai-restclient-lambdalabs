"""
    .. module:: lambdalabssshkey
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsSshKey`
                   hand-authored typed model for a Lambda Labs SSH key.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class LambdalabsSshKey:
    """
        Typed model describing a Lambda Labs SSH key registration.

        Hand-authored from the published Lambda Labs REST documentation.
    """

    def __init__(self, *, identifier: str, name: str, public_key: str,
                 private_key: Optional[str] = None) -> None:
        """
            Initialize a :class:`LambdalabsSshKey`.

            :param identifier: The key identifier assigned by Lambda Labs.
            :param name: The key name.
            :param public_key: The OpenSSH-format public key string.
            :param private_key: The private key, only populated by Lambda
                Labs when the key was generated server-side.

            :returns: ``None``.
        """
        self._identifier = identifier
        self._name = name
        self._public_key = public_key
        self._private_key = private_key
        return

    @property
    def identifier(self) -> str:
        """
            The key identifier.

            :returns: The key identifier string.
        """
        return self._identifier

    @property
    def name(self) -> str:
        """
            The key name.

            :returns: The key name string.
        """
        return self._name

    @property
    def public_key(self) -> str:
        """
            The OpenSSH-format public key.

            :returns: The public key string.
        """
        return self._public_key

    @property
    def private_key(self) -> Optional[str]:
        """
            The private key, if Lambda Labs generated the key server-side.

            :returns: The private key string, or ``None``.
        """
        return self._private_key

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LambdalabsSshKey":
        """
            Construct a :class:`LambdalabsSshKey` from an API payload entry.

            :param data: The raw API payload entry.

            :returns: A populated :class:`LambdalabsSshKey`.
        """
        rtnval = cls(
            identifier=data.get("id", ""),
            name=data.get("name", ""),
            public_key=data.get("public_key", ""),
            private_key=data.get("private_key", None),
        )
        return rtnval
