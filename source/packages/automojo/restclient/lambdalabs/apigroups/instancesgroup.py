"""
    .. module:: instancesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`InstancesGroup` api group
                   exposing the Lambda Labs instances endpoints.

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
from automojo.restclient.lambdalabs.model.lambdalabsinstance import (
    LambdalabsInstance
)
from automojo.restclient.lambdalabs.model.lambdalabsterminationresult import (
    LambdalabsTerminationResult
)
from automojo.restclient.lambdalabs.specs.lambdalabslaunchspec import (
    LambdalabsLaunchSpec
)


class InstancesGroup(RestApiGroup):
    """
        :class:`InstancesGroup` exposes the Lambda Labs instances endpoints —
        list, get, launch, and terminate.
    """

    def list(self, *,
             aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
             ) -> List[LambdalabsInstance]:
        """
            List every instance, following paging cursors transparently.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsInstance` records.
        """
        client = self.client

        def _fetch_page(cursor: Optional[str]) -> Tuple[List[LambdalabsInstance], Optional[str]]:
            leaf = compose_leaf(parts=["instances"])
            params = None
            if cursor is not None:
                params = {"cursor": cursor}
            response = client.request(method="GET", leaf=leaf, params=params,
                                      aspects=aspects)
            raise_for_status(response=response, action="list instances")

            data = extract_data(response=response, action="list instances")
            page_items: List[LambdalabsInstance] = []
            for entry in data:
                page_items.append(LambdalabsInstance.from_dict(entry))

            envelope = safe_json(response=response)
            next_cursor = envelope.get("next_cursor", None)
            return page_items, next_cursor

        rtnval = collect_all_pages(fetch_page=_fetch_page)
        return rtnval

    def get(self, *, instance_id: str,
            aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
            ) -> LambdalabsInstance:
        """
            Retrieve a single instance by id.

            :param instance_id: The Lambda Labs instance identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsInstance` record.
        """
        require_identifier(value=instance_id, name="instance_id")

        client = self.client
        leaf = compose_leaf(parts=["instances", instance_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get instance")

        data = extract_data(response=response, action="get instance")
        rtnval = LambdalabsInstance.from_dict(data)
        return rtnval

    def launch(self, *, spec: LambdalabsLaunchSpec,
               aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
               ) -> List[LambdalabsInstance]:
        """
            Launch one or more instances from a launch spec.

            :param spec: The :class:`LambdalabsLaunchSpec` to launch.
            :param aspects: Behaviour control for the call.

            :returns: A list of launched :class:`LambdalabsInstance`
                records.

            :raises: :class:`SemanticError` when ``spec`` is ``None``.
        """
        if spec is None:
            raise SemanticError("'spec' must be a LambdalabsLaunchSpec.")

        client = self.client
        leaf = compose_leaf(parts=["instance-operations", "launch"])
        response = client.request(method="POST", leaf=leaf,
                                   json_body=spec.to_dict(), aspects=aspects)
        raise_for_status(response=response, action="launch instances")

        data = extract_data(response=response, action="launch instances")

        # Lambda Labs returns either a list of instances or a dict carrying
        # an 'instance_ids' list; both shapes are normalised here.
        rtnval: List[LambdalabsInstance] = []
        if isinstance(data, dict):
            launched_ids = data.get("instance_ids", None)
            if launched_ids is not None:
                for launched_id in launched_ids:
                    rtnval.append(self.get(instance_id=launched_id,
                                            aspects=aspects))
                return rtnval
            instances_payload = data.get("instances", None)
            if instances_payload is not None:
                for entry in instances_payload:
                    rtnval.append(LambdalabsInstance.from_dict(entry))
                return rtnval
            rtnval.append(LambdalabsInstance.from_dict(data))
            return rtnval

        for entry in data:
            rtnval.append(LambdalabsInstance.from_dict(entry))
        return rtnval

    def terminate(self, *, instance_ids: List[str],
                  aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                  ) -> LambdalabsTerminationResult:
        """
            Terminate one or more instances by id.

            Ids that are already terminated are reported in the result's
            ``already_terminated`` list rather than raising.

            :param instance_ids: The instance identifiers to terminate.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsTerminationResult`.

            :raises: :class:`SemanticError` when ``instance_ids`` is
                ``None``.
        """
        if instance_ids is None:
            raise SemanticError("'instance_ids' must be a list of ids.")

        client = self.client
        leaf = compose_leaf(parts=["instance-operations", "terminate"])
        body = {"instance_ids": list(instance_ids)}
        response = client.request(method="POST", leaf=leaf, json_body=body,
                                   aspects=aspects)
        raise_for_status(response=response, action="terminate instances")

        data = extract_data(response=response, action="terminate instances")
        rtnval = LambdalabsTerminationResult.from_dict(
            data, requested_ids=list(instance_ids)
        )
        return rtnval
