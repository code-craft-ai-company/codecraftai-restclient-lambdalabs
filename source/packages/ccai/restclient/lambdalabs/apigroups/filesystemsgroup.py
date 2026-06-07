"""
    .. module:: filesystemsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`FilesystemsGroup` api
                   group exposing the Lambda Labs file-systems endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.lambdalabs.aspectslambdalabs import (
    AspectsLambdalabs, DEFAULT_LAMBDALABS_ASPECTS
)
from ccai.restclient.lambdalabs.apigroups.groupsupport import (
    compose_leaf, extract_data, raise_for_status, require_identifier,
    safe_json
)
from ccai.restclient.lambdalabs.apigroups.pagingsupport import (
    collect_all_pages
)
from ccai.restclient.lambdalabs.model.lambdalabsfilesystem import (
    LambdalabsFilesystem
)


class FilesystemsGroup(RestApiGroup):
    """
        :class:`FilesystemsGroup` exposes the Lambda Labs file-systems
        endpoints — list, create (read-before-create), and delete
        (idempotent).
    """

    def list(self, *,
             aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
             ) -> List[LambdalabsFilesystem]:
        """
            List every persistent file system, following paging cursors.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsFilesystem` records.
        """
        client = self.client

        def _fetch_page(cursor: Optional[str]) -> Tuple[List[LambdalabsFilesystem], Optional[str]]:
            leaf = compose_leaf(parts=["file-systems"])
            params = None
            if cursor is not None:
                params = {"cursor": cursor}
            response = client.request(method="GET", leaf=leaf, params=params,
                                      aspects=aspects)
            raise_for_status(response=response, action="list file systems")

            data = extract_data(response=response, action="list file systems")
            page_items: List[LambdalabsFilesystem] = []
            for entry in data:
                page_items.append(LambdalabsFilesystem.from_dict(entry))

            envelope = safe_json(response=response)
            next_cursor = envelope.get("next_cursor", None)
            return page_items, next_cursor

        rtnval = collect_all_pages(fetch_page=_fetch_page)
        return rtnval

    def create(self, *, name: str, region: str,
               aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
               ) -> LambdalabsFilesystem:
        """
            Create a persistent file system, reusing an existing file system
            of the same name in the same region.

            :param name: The file-system name.
            :param region: The region to create the file system in.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing
                :class:`LambdalabsFilesystem`.
        """
        require_identifier(value=name, name="name")
        require_identifier(value=region, name="region")

        existing = self.list(aspects=aspects)
        for filesystem in existing:
            if filesystem.name == name and filesystem.region == region:
                rtnval = filesystem
                return rtnval

        client = self.client
        leaf = compose_leaf(parts=["file-systems"])
        body: Dict[str, Any] = {"name": name, "region": region}
        response = client.request(method="POST", leaf=leaf, json_body=body,
                                  aspects=aspects)
        raise_for_status(response=response, action="create file system")

        data = extract_data(response=response, action="create file system")
        rtnval = LambdalabsFilesystem.from_dict(data)
        return rtnval

    def delete(self, *, filesystem_id: str,
               aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
               ) -> None:
        """
            Delete a file system by id.  A 404 is treated as already-removed
            so the delete is idempotent.

            :param filesystem_id: The Lambda Labs file-system identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        require_identifier(value=filesystem_id, name="filesystem_id")

        client = self.client
        leaf = compose_leaf(parts=["file-systems", filesystem_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete file system")
        return
