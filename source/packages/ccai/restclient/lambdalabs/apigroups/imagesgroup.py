"""
    .. module:: imagesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ImagesGroup` api group
                   exposing the Lambda Labs images endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import List, Optional, Tuple

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.lambdalabs.aspectslambdalabs import (
    AspectsLambdalabs, DEFAULT_LAMBDALABS_ASPECTS
)
from ccai.restclient.lambdalabs.apigroups.groupsupport import (
    compose_leaf, extract_data, raise_for_status, safe_json
)
from ccai.restclient.lambdalabs.apigroups.pagingsupport import (
    collect_all_pages
)
from ccai.restclient.lambdalabs.model.lambdalabsimage import LambdalabsImage


class ImagesGroup(RestApiGroup):
    """
        :class:`ImagesGroup` exposes the Lambda Labs
        ``GET /api/v1/images`` endpoint, which enumerates the supported
        operating-system images.
    """

    def list(self, *,
             aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
             ) -> List[LambdalabsImage]:
        """
            List every supported Lambda Labs operating-system image.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsImage` records.
        """
        client = self.client

        def _fetch_page(cursor: Optional[str]) -> Tuple[List[LambdalabsImage], Optional[str]]:
            leaf = compose_leaf(parts=["images"])
            params = None
            if cursor is not None:
                params = {"cursor": cursor}
            response = client.request(method="GET", leaf=leaf, params=params,
                                      aspects=aspects)
            raise_for_status(response=response, action="list images")

            data = extract_data(response=response, action="list images")
            page_items: List[LambdalabsImage] = []
            for entry in data:
                page_items.append(LambdalabsImage.from_dict(entry))

            envelope = safe_json(response=response)
            next_cursor = envelope.get("next_cursor", None)
            return page_items, next_cursor

        rtnval = collect_all_pages(fetch_page=_fetch_page)
        return rtnval
