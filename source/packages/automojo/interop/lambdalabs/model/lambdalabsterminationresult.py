"""
    .. module:: lambdalabsterminationresult
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsTerminationResult`
                   hand-authored typed model for a terminate-instances call.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.interop.lambdalabs.model.lambdalabsinstance import (
    LambdalabsInstance
)


class LambdalabsTerminationResult:
    """
        Typed model describing the outcome of a terminate-instances call.

        Lambda Labs returns the set of instances that transitioned to a
        terminating/terminated state.  Identifiers that were already
        terminated are reported in :attr:`already_terminated` so callers
        can treat the operation as idempotent.
    """

    def __init__(self, *,
                 terminated: Optional[List[LambdalabsInstance]] = None,
                 already_terminated: Optional[List[str]] = None) -> None:
        """
            Initialize a :class:`LambdalabsTerminationResult`.

            :param terminated: The instances that were terminated by the
                call.
            :param already_terminated: Instance ids that were already in a
                terminated state before the call.

            :returns: ``None``.
        """
        if terminated is not None:
            self._terminated = list(terminated)
        else:
            self._terminated = []
        if already_terminated is not None:
            self._already_terminated = list(already_terminated)
        else:
            self._already_terminated = []
        return

    @property
    def terminated(self) -> List[LambdalabsInstance]:
        """
            The instances that were terminated by the call.

            :returns: A defensive copy of the terminated instance list.
        """
        rtnval = list(self._terminated)
        return rtnval

    @property
    def already_terminated(self) -> List[str]:
        """
            Instance ids that were already terminated before the call.

            :returns: A defensive copy of the already-terminated id list.
        """
        rtnval = list(self._already_terminated)
        return rtnval

    def status_for(self, *, instance_id: str) -> str:
        """
            Return the per-id termination status.

            :param instance_id: The instance id to look up.

            :returns: ``"terminated"`` when the call terminated the id,
                ``"already-terminated"`` when it was already terminated,
                ``"unknown"`` otherwise.
        """
        for instance in self._terminated:
            if instance.identifier == instance_id:
                rtnval = "terminated"
                return rtnval
        if instance_id in self._already_terminated:
            rtnval = "already-terminated"
            return rtnval
        rtnval = "unknown"
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any],
                  requested_ids: Optional[List[str]] = None
                  ) -> "LambdalabsTerminationResult":
        """
            Construct a :class:`LambdalabsTerminationResult` from an API
            payload.

            :param data: The raw API payload.
            :param requested_ids: The instance ids the caller requested;
                ids absent from the terminated list are classified as
                already-terminated.

            :returns: A populated :class:`LambdalabsTerminationResult`.
        """
        terminated_payload = data.get("terminated_instances", None)
        if terminated_payload is None:
            terminated_payload = []

        terminated: List[LambdalabsInstance] = []
        terminated_ids: List[str] = []
        for entry in terminated_payload:
            instance = LambdalabsInstance.from_dict(entry)
            terminated.append(instance)
            terminated_ids.append(instance.identifier)

        already: List[str] = []
        if requested_ids is not None:
            for requested_id in requested_ids:
                if requested_id not in terminated_ids:
                    already.append(requested_id)

        rtnval = cls(terminated=terminated, already_terminated=already)
        return rtnval
