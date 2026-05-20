"""
    .. module:: clustersgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ClustersGroup` api group
                   exposing the Lambda Labs 1-click-clusters endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional, Tuple

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.lambdalabs.aspectslambdalabs import (
    AspectsLambdalabs, DEFAULT_LAMBDALABS_ASPECTS
)
from automojo.restclient.lambdalabs.apigroups.groupsupport import (
    compose_leaf, extract_data, raise_for_status, require_identifier,
    safe_json
)
from automojo.restclient.lambdalabs.apigroups.pagingsupport import (
    collect_all_pages
)
from automojo.restclient.lambdalabs.model.lambdalabscluster import (
    LambdalabsCluster
)
from automojo.restclient.lambdalabs.specs.lambdalabsclusterspec import (
    LambdalabsClusterSpec
)


class ClustersGroup(RestApiGroup):
    """
        :class:`ClustersGroup` exposes the Lambda Labs 1-click-clusters
        endpoints — list, create, get, and delete (idempotent).
    """

    def list(self, *,
             aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
             ) -> List[LambdalabsCluster]:
        """
            List every 1-click cluster, following paging cursors.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsCluster` records.
        """
        client = self.client

        def _fetch_page(cursor: Optional[str]) -> Tuple[List[LambdalabsCluster], Optional[str]]:
            leaf = compose_leaf(parts=["1-click-clusters"])
            params = None
            if cursor is not None:
                params = {"cursor": cursor}
            response = client.request(method="GET", leaf=leaf, params=params,
                                      aspects=aspects)
            raise_for_status(response=response, action="list clusters")

            data = extract_data(response=response, action="list clusters")
            page_items: List[LambdalabsCluster] = []
            for entry in data:
                page_items.append(LambdalabsCluster.from_dict(entry))

            envelope = safe_json(response=response)
            next_cursor = envelope.get("next_cursor", None)
            return page_items, next_cursor

        rtnval = collect_all_pages(fetch_page=_fetch_page)
        return rtnval

    def create(self, *, spec: LambdalabsClusterSpec,
               aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
               ) -> LambdalabsCluster:
        """
            Create a 1-click cluster from a cluster spec.

            :param spec: The :class:`LambdalabsClusterSpec` to create.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsCluster` record.

            :raises: :class:`SemanticError` when ``spec`` is ``None``.
        """
        if spec is None:
            raise SemanticError("'spec' must be a LambdalabsClusterSpec.")

        client = self.client
        leaf = compose_leaf(parts=["1-click-clusters"])
        response = client.request(method="POST", leaf=leaf,
                                   json_body=spec.to_dict(), aspects=aspects)
        raise_for_status(response=response, action="create cluster")

        data = extract_data(response=response, action="create cluster")
        rtnval = LambdalabsCluster.from_dict(data)
        return rtnval

    def get(self, *, cluster_id: str,
            aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
            ) -> LambdalabsCluster:
        """
            Retrieve a single 1-click cluster by id.

            :param cluster_id: The Lambda Labs cluster identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsCluster` record.
        """
        require_identifier(value=cluster_id, name="cluster_id")

        client = self.client
        leaf = compose_leaf(parts=["1-click-clusters", cluster_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get cluster")

        data = extract_data(response=response, action="get cluster")
        rtnval = LambdalabsCluster.from_dict(data)
        return rtnval

    def delete(self, *, cluster_id: str,
               aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
               ) -> None:
        """
            Delete a 1-click cluster by id.  A 404 is treated as
            already-removed so the delete is idempotent.

            :param cluster_id: The Lambda Labs cluster identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        require_identifier(value=cluster_id, name="cluster_id")

        client = self.client
        leaf = compose_leaf(parts=["1-click-clusters", cluster_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete cluster")
        return
