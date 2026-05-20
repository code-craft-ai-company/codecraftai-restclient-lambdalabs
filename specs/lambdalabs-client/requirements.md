# Requirements

## Introduction

The `lambdalabs-client` feature provides a REST client for Lambda Labs'
cloud API. The API surface is small and IaaS-shaped: instances, SSH keys,
file systems, instance types, and 1-click clusters. This client exposes
exactly those primitives so the `venue-lambdalabs` provisioner in
`automojo-provisioning` can implement the neutral
`plan / apply / destroy / inventory` lifecycle.

The client is built on `RestClientBase` from `automojo-restclient-base`,
authenticates with a typed `LambdalabsApiKeyCredential`, and exposes
`aspects: AspectsRest = DEFAULT_LAMBDALABS_ASPECTS` on every behaviour-bearing
call. The client does not interpret the neutral provisioning model directly —
that mapping lives in the provisioner.

---

## Requirements

### Requirement 1: Authenticate Against the Lambda Labs API

**User Story:** As a provisioner, I want to authenticate using a typed
API-key credential so that every subsequent call carries the correct
authorization header.

#### Acceptance Criteria

1. WHEN the client is constructed with a `LambdalabsApiKeyCredential` THE
   SYSTEM SHALL configure `RestClientBase` with Bearer-token authentication
   sourced from the credential.
2. WHEN the credential is missing or its key is empty THE SYSTEM SHALL
   raise `ConfigurationError` before any HTTP call.
3. WHEN an API call returns HTTP 401 or 403 THE SYSTEM SHALL reclassify
   the error into `LambdalabsAuthenticationError`.

### Requirement 2: Enumerate Instance Types and Regions

**User Story:** As a provisioner, I want to list available instance types
and their per-region availability so that I can resolve a neutral
`CloudAcceleratorSpec` to a concrete Lambda Labs SKU at plan time.

#### Acceptance Criteria

1. WHEN the caller invokes `list_instance_types(aspects)` THE SYSTEM SHALL
   return a list of `LambdalabsInstanceType` records carrying GPU model,
   GPU count, vCPU, memory, price, and a `regions_with_capacity` list.
2. WHEN a requested instance-type name does not exist THE SYSTEM SHALL
   raise `LambdalabsInstanceTypeNotFoundError`.

### Requirement 3: Manage SSH Keys

**User Story:** As a provisioner bootstrapping access to launched
instances, I want to register, list, and delete SSH keys so that
instances accept the provisioner's key without manual setup.

#### Acceptance Criteria

1. WHEN the caller invokes `register_ssh_key(name, public_key, aspects)`
   THE SYSTEM SHALL POST the key and return a `LambdalabsSshKey` record.
2. WHEN a key with the same name already exists THE SYSTEM SHALL return
   the existing record without creating a duplicate.
3. WHEN the caller invokes `list_ssh_keys(aspects)` THE SYSTEM SHALL
   return all keys, following any paging cursors transparently.
4. WHEN the caller invokes `delete_ssh_key(key_id, aspects)` against an
   unknown key id THE SYSTEM SHALL succeed as a no-op (idempotent delete).

### Requirement 4: Manage File Systems

**User Story:** As a provisioner staging shared storage for a training
job, I want to create, list, attach, and delete persistent file systems
so that the `CloudSharedFilesystem` model can be honoured on Lambda Labs.

#### Acceptance Criteria

1. WHEN the caller invokes `create_filesystem(name, region, aspects)`
   THE SYSTEM SHALL POST the request and return a `LambdalabsFilesystem`
   record.
2. WHEN a filesystem with the same name in the same region already exists
   THE SYSTEM SHALL return the existing record (read-before-create).
3. WHEN the caller invokes `list_filesystems(aspects)` THE SYSTEM SHALL
   return all filesystems, following paging cursors.
4. WHEN the caller invokes `delete_filesystem(filesystem_id, aspects)`
   THE SYSTEM SHALL DELETE the resource. WHEN the id is unknown the call
   SHALL succeed as a no-op.

### Requirement 5: Launch, Inspect, and Terminate Instances

**User Story:** As a provisioner implementing the apply pipeline's compute
stage, I want a small launch/inspect/terminate surface so that single-VM
provisioning lands end-to-end.

#### Acceptance Criteria

1. WHEN the caller invokes `launch_instances(spec, aspects)` where `spec`
   is a `LambdalabsLaunchSpec` (region, instance_type_name, ssh_key_names,
   filesystem_names, name, quantity) THE SYSTEM SHALL POST the request and
   return a list of `LambdalabsInstance` records with assigned ids.
2. WHEN the request would exceed the account's quota THE SYSTEM SHALL
   reclassify the resulting HTTP error into `LambdalabsQuotaExceededError`.
3. WHEN the caller invokes `get_instance(instance_id, aspects)` THE SYSTEM
   SHALL return the current `LambdalabsInstance` record including public/private
   IPs, status, and SSH host once available.
4. WHEN the caller invokes `list_instances(aspects)` THE SYSTEM SHALL
   return all instances, following paging cursors.
5. WHEN the caller invokes `terminate_instances(instance_ids, aspects)`
   THE SYSTEM SHALL POST the termination request and return a
   `LambdalabsTerminationResult`. WHEN any id is already terminated the
   call SHALL succeed and SHALL report the per-id status in the result.

### Requirement 6: Manage 1-Click Clusters

**User Story:** As a provisioner planning a multi-node training job, I
want to create, inspect, and tear down 1-click clusters so that
InfiniBand-connected node groups can be expressed in a single API call.

#### Acceptance Criteria

1. WHEN the caller invokes `create_cluster(spec, aspects)` where `spec`
   is a `LambdalabsClusterSpec` THE SYSTEM SHALL POST the request and
   return a `LambdalabsCluster` record.
2. WHEN the caller invokes `get_cluster(cluster_id, aspects)` THE SYSTEM
   SHALL return the current cluster record including member instance ids
   and interconnect status.
3. WHEN the caller invokes `delete_cluster(cluster_id, aspects)` against
   an unknown id THE SYSTEM SHALL succeed as a no-op.

### Requirement 7: Wait Until an Instance Is Running

**User Story:** As a provisioner, I want a typed waiter so that the
verify stage of `apply` can block on instance readiness with caller-controlled
intervals and timeouts.

#### Acceptance Criteria

1. WHEN the caller invokes `wait_until_running(instance_id, aspects)`
   THE SYSTEM SHALL poll `get_instance` at the interval dictated by aspects
   until status is `active` or the aspects timeout elapses.
2. WHEN the timeout elapses THE SYSTEM SHALL raise `TimeoutError` with
   the instance id and last observed status.
3. WHEN the instance enters a terminal-failed state THE SYSTEM SHALL
   raise `LambdalabsInstanceFailedError` with the failure reason.

### Requirement 8: Image Lookup

**User Story:** As a provisioner resolving a neutral `CloudImage`, I want
to enumerate the operating-system images Lambda Labs supports so that
image-family lookups can succeed at plan time.

#### Acceptance Criteria

1. WHEN the caller invokes `list_images(aspects)` THE SYSTEM SHALL return
   a list of `LambdalabsImage` records with name, family, version, and
   architecture.

### Requirement 9: URL Composition for Nested Resources

**User Story:** As a maintainer, I want URL composition to be total,
unambiguous, and percent-encoded per segment.

#### Acceptance Criteria

1. WHEN any client method composes a URL THE SYSTEM SHALL percent-encode
   each path segment independently.
2. WHEN any identifier is empty or `None` THE SYSTEM SHALL raise
   `SemanticError` before issuing the request.

### Requirement 10: Aspects on Every Behaviour-Bearing Call

**User Story:** As a caller, I want consistent control over retries,
timeouts, backoff, and logging.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest = DEFAULT_LAMBDALABS_ASPECTS`
   as a named-only parameter on every I/O method.
2. THE SYSTEM SHALL never apply behaviour-modifying decorators.
3. WHEN a transient HTTP error occurs THE SYSTEM SHALL retry per `aspects`
   policy and SHALL surface the final error unchanged if the budget is exhausted.
