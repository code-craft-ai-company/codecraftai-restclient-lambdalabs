"""
    .. module:: sshkeysgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SshKeysGroup` api group
                   exposing the Lambda Labs ssh-keys endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.lambdalabs.aspectslambdalabs import (
    AspectsLambdalabs, DEFAULT_LAMBDALABS_ASPECTS
)
from automojo.interop.lambdalabs.apigroups.groupsupport import (
    compose_leaf, extract_data, raise_for_status, require_identifier,
    safe_json
)
from automojo.interop.lambdalabs.apigroups.pagingsupport import (
    collect_all_pages
)
from automojo.interop.lambdalabs.model.lambdalabssshkey import LambdalabsSshKey


class SshKeysGroup(RestApiGroup):
    """
        :class:`SshKeysGroup` exposes the Lambda Labs ssh-keys endpoints —
        list, register (idempotent), and delete (idempotent).
    """

    def list(self, *,
             aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
             ) -> List[LambdalabsSshKey]:
        """
            List every registered SSH key, following any paging cursors.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsSshKey` records.
        """
        client = self.client

        def _fetch_page(cursor: Optional[str]) -> Tuple[List[LambdalabsSshKey], Optional[str]]:
            leaf = compose_leaf(parts=["ssh-keys"])
            params = None
            if cursor is not None:
                params = {"cursor": cursor}
            response = client.request(method="GET", leaf=leaf, params=params,
                                      aspects=aspects)
            raise_for_status(response=response, action="list ssh keys")

            data = extract_data(response=response, action="list ssh keys")
            page_items: List[LambdalabsSshKey] = []
            for entry in data:
                page_items.append(LambdalabsSshKey.from_dict(entry))

            envelope = safe_json(response=response)
            next_cursor = envelope.get("next_cursor", None)
            return page_items, next_cursor

        rtnval = collect_all_pages(fetch_page=_fetch_page)
        return rtnval

    def register(self, *, name: str, public_key: str,
                 aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                 ) -> LambdalabsSshKey:
        """
            Register an SSH key, reusing an existing key with the same name.

            The call lists the existing keys first; when a key with the same
            name is already registered it is returned unchanged so the
            provisioner's ``apply`` is safe to rerun.

            :param name: The SSH key name.
            :param public_key: The OpenSSH-format public key string.
            :param aspects: Behaviour control for the call.

            :returns: The registered or pre-existing
                :class:`LambdalabsSshKey`.
        """
        require_identifier(value=name, name="name")
        require_identifier(value=public_key, name="public_key")

        existing = self.list(aspects=aspects)
        for key in existing:
            if key.name == name:
                rtnval = key
                return rtnval

        client = self.client
        leaf = compose_leaf(parts=["ssh-keys"])
        body: Dict[str, Any] = {"name": name, "public_key": public_key}
        response = client.request(method="POST", leaf=leaf, json_body=body,
                                  aspects=aspects)
        raise_for_status(response=response, action="register ssh key")

        data = extract_data(response=response, action="register ssh key")
        rtnval = LambdalabsSshKey.from_dict(data)
        return rtnval

    def delete(self, *, key_id: str,
               aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
               ) -> None:
        """
            Delete an SSH key by id.  A 404 is treated as already-removed so
            the delete is idempotent.

            :param key_id: The Lambda Labs SSH key identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        require_identifier(value=key_id, name="key_id")

        client = self.client
        leaf = compose_leaf(parts=["ssh-keys", key_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete ssh key")
        return
