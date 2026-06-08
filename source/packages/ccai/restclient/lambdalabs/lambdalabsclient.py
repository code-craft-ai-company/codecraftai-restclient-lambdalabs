"""
    .. module:: lambdalabsclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`LambdalabsClient` REST
                   client for the Lambda Labs Cloud API
                   (``cloud.lambdalabs.com/api/v1/``).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import json
import os
import time

from typing import Any, Dict, List, Optional, Union

from requests import Response, Session

from ccai.errors.exceptions import ConfigurationError, SemanticError

from ccai.credentials.basecredential import BaseCredential
from ccai.credentials.lambdalabsapikeycredential import (
    LambdalabsApiKeyCredential
)

from ccai.restclient.base.restclientbase import RestClientBase

from ccai.restclient.lambdalabs.aspectslambdalabs import (
    AspectsLambdalabs, DEFAULT_LAMBDALABS_ASPECTS
)
from ccai.restclient.lambdalabs.apigroups.clustersgroup import ClustersGroup
from ccai.restclient.lambdalabs.apigroups.filesystemsgroup import (
    FilesystemsGroup
)
from ccai.restclient.lambdalabs.apigroups.imagesgroup import ImagesGroup
from ccai.restclient.lambdalabs.apigroups.instancesgroup import InstancesGroup
from ccai.restclient.lambdalabs.apigroups.instancetypesgroup import (
    InstanceTypesGroup
)
from ccai.restclient.lambdalabs.apigroups.sshkeysgroup import SshKeysGroup
from ccai.restclient.lambdalabs.exceptions.lambdalabserrors import (
    LambdalabsInstanceFailedError
)
from ccai.restclient.lambdalabs.model.lambdalabscluster import (
    LambdalabsCluster
)
from ccai.restclient.lambdalabs.model.lambdalabsfilesystem import (
    LambdalabsFilesystem
)
from ccai.restclient.lambdalabs.model.lambdalabsimage import LambdalabsImage
from ccai.restclient.lambdalabs.model.lambdalabsinstance import (
    LambdalabsInstance
)
from ccai.restclient.lambdalabs.model.lambdalabsinstancetype import (
    LambdalabsInstanceType
)
from ccai.restclient.lambdalabs.model.lambdalabssshkey import LambdalabsSshKey
from ccai.restclient.lambdalabs.model.lambdalabsterminationresult import (
    LambdalabsTerminationResult
)
from ccai.restclient.lambdalabs.specs.lambdalabsclusterspec import (
    LambdalabsClusterSpec
)
from ccai.restclient.lambdalabs.specs.lambdalabslaunchspec import (
    LambdalabsLaunchSpec
)


LAMBDALABS_API_HOST = "cloud.lambdalabs.com"


class LambdalabsClient(RestClientBase):
    """
        :class:`LambdalabsClient` is the typed, aspect-driven REST client
        for the Lambda Labs Cloud API.  It is built on :class:`RestClientBase`
        and authenticates with a typed :class:`LambdalabsApiKeyCredential`
        via a Bearer-token ``Authorization`` header.

        The client exposes its surface through six api groups
        (:attr:`instance_types`, :attr:`images`, :attr:`ssh_keys`,
        :attr:`filesystems`, :attr:`instances`, :attr:`clusters`) and
        additionally provides convenience facade methods that delegate to
        the groups so the ``venue-lambdalabs`` provisioner has a flat
        surface to call.

        All behaviour-bearing methods accept
        ``aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS`` as a
        named-only parameter; no behaviour-modifying decorators are used.
    """

    def __init__(self, *, credential: BaseCredential,
                 host: str = LAMBDALABS_API_HOST,
                 aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                 ) -> None:
        """
            Initialize the Lambda Labs REST client.

            :param credential: A :class:`LambdalabsApiKeyCredential`.
            :param host: Override host name for the REST endpoint.
            :param aspects: Default :class:`AspectsLambdalabs` applied when
                a call omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`ConfigurationError` when ``credential`` is not
                a :class:`LambdalabsApiKeyCredential` or carries no token.
        """
        if not isinstance(credential, LambdalabsApiKeyCredential):
            err_msg_lines = [
                "LambdalabsClient requires a LambdalabsApiKeyCredential."
            ]
            err_msg_lines.append("EXPECTED: LambdalabsApiKeyCredential")
            err_msg_lines.append(
                "FOUND: {}".format(type(credential).__name__)
            )
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        token = credential.token
        if token is None or len(token) == 0:
            raise ConfigurationError(
                "LambdalabsClient requires a credential carrying a "
                "non-empty API-key token."
            )

        super().__init__(host=host, credential=credential, aspects=aspects)

        self._token: str = token

        self._instance_types = InstanceTypesGroup(self)
        self._images = ImagesGroup(self)
        self._ssh_keys = SshKeysGroup(self)
        self._filesystems = FilesystemsGroup(self)
        self._instances = InstancesGroup(self)
        self._clusters = ClustersGroup(self)
        return

    # ------------------------------------------------------------------
    # API groups
    # ------------------------------------------------------------------

    @property
    def instance_types(self) -> InstanceTypesGroup:
        """
            The instance-types api group.

            :returns: The :class:`InstanceTypesGroup` instance.
        """
        return self._instance_types

    @property
    def images(self) -> ImagesGroup:
        """
            The images api group.

            :returns: The :class:`ImagesGroup` instance.
        """
        return self._images

    @property
    def ssh_keys(self) -> SshKeysGroup:
        """
            The ssh-keys api group.

            :returns: The :class:`SshKeysGroup` instance.
        """
        return self._ssh_keys

    @property
    def filesystems(self) -> FilesystemsGroup:
        """
            The file-systems api group.

            :returns: The :class:`FilesystemsGroup` instance.
        """
        return self._filesystems

    @property
    def instances(self) -> InstancesGroup:
        """
            The instances api group.

            :returns: The :class:`InstancesGroup` instance.
        """
        return self._instances

    @property
    def clusters(self) -> ClustersGroup:
        """
            The 1-click-clusters api group.

            :returns: The :class:`ClustersGroup` instance.
        """
        return self._clusters

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def request(self, *, method: str, leaf: str,
                params: Optional[Dict[str, str]] = None,
                json_body: Optional[Union[Dict[str, Any], list]] = None,
                headers: Optional[Dict[str, str]] = None,
                aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                ) -> Response:
        """
            Issue a single REST call against the Lambda Labs Cloud API.

            The call attaches the Bearer-token ``Authorization`` header and
            serializes ``json_body`` as raw JSON.  HTTP-error reclassification
            is performed by the api groups via ``raise_for_status``.

            :param method: HTTP method to invoke.
            :param leaf: API leaf path beginning with ``/``.
            :param params: Optional query-string parameters.
            :param json_body: Optional dict/list serialized as the body.
            :param headers: Optional additional request headers.
            :param aspects: Behaviour-control aspects for the call.

            :returns: The :class:`Response` object from the call.
        """
        session = self._authenticated_session()
        call_url = self._format_call_url(leaf)
        send_timeouts = (aspects.connection_timeout,
                         aspects.inactivity_timeout)

        body_bytes: Optional[bytes] = None
        send_headers: Dict[str, str] = {}
        if headers is not None:
            send_headers.update(headers)

        if json_body is not None:
            body_bytes = json.dumps(json_body).encode("utf-8")
            if "Content-Type" not in send_headers:
                send_headers["Content-Type"] = "application/json"

        response: Response = session.request(method=method, url=call_url,
                                              params=params, data=body_bytes,
                                              headers=send_headers,
                                              timeout=send_timeouts,
                                              verify=self._verify_certificate)
        rtnval = response
        return rtnval

    def _authenticated_session(self) -> Session:
        """
            Build a :class:`Session` carrying the Bearer-token header.

            :returns: A :class:`Session` ready to issue authenticated calls.
        """
        session = Session()
        session.verify = self._verify_certificate
        session.headers.update({
            "Authorization": "Bearer {}".format(self._token),
            "Accept": "application/json",
        })

        rtnval = session
        return rtnval

    # ------------------------------------------------------------------
    # Convenience facade — instance types & images
    # ------------------------------------------------------------------

    def list_instance_types(self, *,
                            aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                            ) -> List[LambdalabsInstanceType]:
        """
            Enumerate every Lambda Labs instance type with region capacity.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsInstanceType` records.
        """
        rtnval = self._instance_types.list(aspects=aspects)
        return rtnval

    def get_instance_type(self, *, name: str,
                          aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                          ) -> LambdalabsInstanceType:
        """
            Retrieve a single instance type by name.

            :param name: The instance-type slug.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsInstanceType` record.

            :raises: :class:`LambdalabsInstanceTypeNotFoundError`.
        """
        rtnval = self._instance_types.get(name=name, aspects=aspects)
        return rtnval

    def list_images(self, *,
                    aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                    ) -> List[LambdalabsImage]:
        """
            Enumerate the supported Lambda Labs operating-system images.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsImage` records.
        """
        rtnval = self._images.list(aspects=aspects)
        return rtnval

    # ------------------------------------------------------------------
    # Convenience facade — ssh keys
    # ------------------------------------------------------------------

    def register_ssh_key(self, *, name: str, public_key: str,
                         aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                         ) -> LambdalabsSshKey:
        """
            Register an SSH key, reusing an existing key of the same name.

            :param name: The SSH key name.
            :param public_key: The OpenSSH-format public key string.
            :param aspects: Behaviour control for the call.

            :returns: The registered or pre-existing
                :class:`LambdalabsSshKey`.
        """
        rtnval = self._ssh_keys.register(name=name, public_key=public_key,
                                         aspects=aspects)
        return rtnval

    def list_ssh_keys(self, *,
                      aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                      ) -> List[LambdalabsSshKey]:
        """
            Enumerate every registered SSH key.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsSshKey` records.
        """
        rtnval = self._ssh_keys.list(aspects=aspects)
        return rtnval

    def delete_ssh_key(self, *, key_id: str,
                       aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                       ) -> None:
        """
            Delete an SSH key by id (idempotent).

            :param key_id: The Lambda Labs SSH key identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        self._ssh_keys.delete(key_id=key_id, aspects=aspects)
        return

    # ------------------------------------------------------------------
    # Convenience facade — file systems
    # ------------------------------------------------------------------

    def create_filesystem(self, *, name: str, region: str,
                          aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                          ) -> LambdalabsFilesystem:
        """
            Create a persistent file system, reusing an existing one of the
            same name in the same region.

            :param name: The file-system name.
            :param region: The region to create the file system in.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsFilesystem` record.
        """
        rtnval = self._filesystems.create(name=name, region=region,
                                          aspects=aspects)
        return rtnval

    def list_filesystems(self, *,
                         aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                         ) -> List[LambdalabsFilesystem]:
        """
            Enumerate every persistent file system.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsFilesystem` records.
        """
        rtnval = self._filesystems.list(aspects=aspects)
        return rtnval

    def delete_filesystem(self, *, filesystem_id: str,
                          aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                          ) -> None:
        """
            Delete a file system by id (idempotent).

            :param filesystem_id: The Lambda Labs file-system identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        self._filesystems.delete(filesystem_id=filesystem_id, aspects=aspects)
        return

    # ------------------------------------------------------------------
    # Convenience facade — instances
    # ------------------------------------------------------------------

    def launch_instances(self, *, spec: LambdalabsLaunchSpec,
                         aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                         ) -> List[LambdalabsInstance]:
        """
            Launch one or more instances from a launch spec.

            :param spec: The :class:`LambdalabsLaunchSpec` to launch.
            :param aspects: Behaviour control for the call.

            :returns: A list of launched :class:`LambdalabsInstance`
                records.

            :raises: :class:`LambdalabsQuotaExceededError`.
        """
        rtnval = self._instances.launch(spec=spec, aspects=aspects)
        return rtnval

    def get_instance(self, *, instance_id: str,
                     aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                     ) -> LambdalabsInstance:
        """
            Retrieve a single instance by id.

            :param instance_id: The Lambda Labs instance identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsInstance` record.
        """
        rtnval = self._instances.get(instance_id=instance_id, aspects=aspects)
        return rtnval

    def list_instances(self, *,
                       aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                       ) -> List[LambdalabsInstance]:
        """
            Enumerate every instance.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsInstance` records.
        """
        rtnval = self._instances.list(aspects=aspects)
        return rtnval

    def terminate_instances(self, *, instance_ids: List[str],
                            aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                            ) -> LambdalabsTerminationResult:
        """
            Terminate one or more instances by id.

            :param instance_ids: The instance identifiers to terminate.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsTerminationResult`.
        """
        rtnval = self._instances.terminate(instance_ids=instance_ids,
                                           aspects=aspects)
        return rtnval

    # ------------------------------------------------------------------
    # Convenience facade — 1-click clusters
    # ------------------------------------------------------------------

    def list_clusters(self, *,
                      aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                      ) -> List[LambdalabsCluster]:
        """
            Enumerate every 1-click cluster.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`LambdalabsCluster` records.
        """
        rtnval = self._clusters.list(aspects=aspects)
        return rtnval

    def create_cluster(self, *, spec: LambdalabsClusterSpec,
                        aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                        ) -> LambdalabsCluster:
        """
            Create a 1-click cluster from a cluster spec.

            :param spec: The :class:`LambdalabsClusterSpec` to create.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsCluster` record.
        """
        rtnval = self._clusters.create(spec=spec, aspects=aspects)
        return rtnval

    def get_cluster(self, *, cluster_id: str,
                    aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                    ) -> LambdalabsCluster:
        """
            Retrieve a single 1-click cluster by id.

            :param cluster_id: The Lambda Labs cluster identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`LambdalabsCluster` record.
        """
        rtnval = self._clusters.get(cluster_id=cluster_id, aspects=aspects)
        return rtnval

    def delete_cluster(self, *, cluster_id: str,
                       aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                       ) -> None:
        """
            Delete a 1-click cluster by id (idempotent).

            :param cluster_id: The Lambda Labs cluster identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        self._clusters.delete(cluster_id=cluster_id, aspects=aspects)
        return

    # ------------------------------------------------------------------
    # Waiter
    # ------------------------------------------------------------------

    def wait_until_running(self, *, instance_id: str,
                           aspects: AspectsLambdalabs = DEFAULT_LAMBDALABS_ASPECTS
                           ) -> LambdalabsInstance:
        """
            Poll an instance until it reaches the ``active`` state.

            The waiter polls :meth:`get_instance` at the interval dictated
            by ``aspects.wait_running_interval_seconds`` until the instance
            status is ``active`` or ``aspects.wait_running_timeout_seconds``
            elapses.

            :param instance_id: The Lambda Labs instance identifier.
            :param aspects: Behaviour control carrying the waiter timeout
                and polling interval.

            :returns: The :class:`LambdalabsInstance` once it is active.

            :raises: :class:`SemanticError` when ``instance_id`` is empty,
                :class:`LambdalabsInstanceFailedError` when the instance
                enters a terminal-failed state, and :class:`TimeoutError`
                when the timeout elapses before the instance is active.
        """
        if instance_id is None or len(instance_id) == 0:
            raise SemanticError("'instance_id' must be a non-empty string.")

        timeout = aspects.wait_running_timeout_seconds
        interval = aspects.wait_running_interval_seconds

        start_time = time.time()
        last_status = "unknown"

        while True:
            instance = self.get_instance(instance_id=instance_id,
                                         aspects=aspects)
            last_status = instance.status

            if instance.is_active:
                rtnval = instance
                return rtnval

            if instance.is_terminal_failed:
                err_msg_lines = [
                    "Lambda Labs instance entered a terminal-failed state."
                ]
                err_msg_lines.append("INSTANCE: {}".format(instance_id))
                err_msg_lines.append("STATUS: {}".format(last_status))
                err_msg = os.linesep.join(err_msg_lines)
                raise LambdalabsInstanceFailedError(err_msg)

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                err_msg_lines = [
                    "Timed out waiting for Lambda Labs instance to become "
                    "active."
                ]
                err_msg_lines.append("INSTANCE: {}".format(instance_id))
                err_msg_lines.append(
                    "LAST STATUS: {}".format(last_status)
                )
                err_msg_lines.append("TIMEOUT: {}".format(timeout))
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg)

            time.sleep(interval)
        return rtnval
