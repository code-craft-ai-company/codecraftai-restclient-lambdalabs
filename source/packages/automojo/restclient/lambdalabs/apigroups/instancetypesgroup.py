"""
    .. module:: instancetypesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`InstanceTypesGroup` api
                   group exposing the Lambda Labs instance-types endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Dict, List

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.lambdalabs.aspectslambdalabs import (
    AspectsLambdalabs, DEFAULT_LAMBDALABS_ASPECTS
)
from automojo.restclient.lambdalabs.apigroups.groupsupport import (
    compose_leaf, extract_data, raise_for_status
)
from automojo.restclient.lambdalabs.exceptions.lambdalabserrors import (
    LambdalabsInstanceTypeNotFoundError
)
from automojo.restclient.lambdalabs.model.lambdalabsinstancetype import (
    LambdalabsInstanceType
)


class InstanceTypesGroup(RestApiGroup):
    """
        :class:`InstanceTypesGroup` exposes the Lambda Labs
        ``GET /api/v1/instance-types`` endpoint, which enumerates every
        instance type and its per-region capacity.
    """

    def list(self, *,
             aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
             ) -> List[LambdalabsInstanceType]:
        """
            List every Lambda Labs instance type with region capacity.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsInstanceType` records.
        """
        client = self.client
        leaf = compose_leaf(parts=["instance-types"])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="list instance types")

        data = extract_data(response=response, action="list instance types")

        rtnval: List[LambdalabsInstanceType] = []
        # The instance-types endpoint returns a mapping keyed by type name.
        if isinstance(data, dict):
            for type_name in sorted(data.keys()):
                entry = data[type_name]
                rtnval.append(LambdalabsInstanceType.from_dict(entry))
        else:
            for entry in data:
                rtnval.append(LambdalabsInstanceType.from_dict(entry))

        return rtnval

    def get(self, *, name: str,
            aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
            ) -> LambdalabsInstanceType:
        """
            Retrieve a single instance type by name.

            :param name: The instance-type slug.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsInstanceType` record.

            :raises: :class:`LambdalabsInstanceTypeNotFoundError` when the
                instance-type name is not present in the catalog.
        """
        types = self.list(aspects=aspects)
        for entry in types:
            if entry.name == name:
                rtnval = entry
                return rtnval

        known: List[str] = []
        for entry in types:
            known.append(entry.name)
        err_msg = (
            "Lambda Labs instance type {!r} was not found. "
            "KNOWN: {}".format(name, ", ".join(sorted(known)))
        )
        raise LambdalabsInstanceTypeNotFoundError(err_msg)
