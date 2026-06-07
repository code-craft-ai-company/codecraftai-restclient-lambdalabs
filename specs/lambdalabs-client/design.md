# Design

## Overview

`LambdalabsClient` is a `RestClientBase` subclass that talks to the Lambda
Labs cloud API. The surface is small and IaaS-shaped — instance types,
images, SSH keys, file systems, instances, 1-click clusters — and is
exposed as a set of `RestApiGroup`-derived API groups.

All calls accept `aspects: AspectsRest = DEFAULT_LAMBDALABS_ASPECTS`.
Credentials are typed (`LambdalabsApiKeyCredential`). The client supports
idempotent reads-before-create for SSH keys and file systems so the
provisioner's `apply` is safe to rerun.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  codecraftai-provisioning / venues / lambdalabs           │
│  (CloudProvisioner lifecycle)                          │
└──────────┬─────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  LambdalabsClient (this package)                       │
│   ─ RestClientBase                                     │
│   ─ AspectsRest on every op                            │
│   ─ API groups: instance-types, images, ssh-keys,      │
│     filesystems, instances, clusters                   │
└──────────┬─────────────────────────────────────────────┘
           │ HTTPS, Bearer token
           ▼
┌────────────────────────────────────────────────────────┐
│  cloud.lambdalabs.com  (REST)                          │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`model/`:
- `lambdalabsinstancetype.py`
- `lambdalabsimage.py`
- `lambdalabssshkey.py`
- `lambdalabsfilesystem.py`
- `lambdalabsinstance.py`
- `lambdalabscluster.py`
- `lambdalabsterminationresult.py`

`specs/`:
- `lambdalabslaunchspec.py`
- `lambdalabsclusterspec.py`

Exceptions:
- `LambdalabsAuthenticationError`
- `LambdalabsInstanceTypeNotFoundError`
- `LambdalabsQuotaExceededError`
- `LambdalabsInstanceFailedError`

---

## Module Layout

```
source/packages/ccai/restclient/lambdalabs/
├── __init__.py
├── lambdalabsclient.py
├── aspectslambdalabs.py
├── apigroups/
│   ├── instancetypesgroup.py
│   ├── imagesgroup.py
│   ├── sshkeysgroup.py
│   ├── filesystemsgroup.py
│   ├── instancesgroup.py
│   └── clustersgroup.py
├── model/
├── specs/
└── exceptions/
```

---

## See Also

- `codecraftai-restclient-base/specs/restapigroup-enhancements/`
- `codecraftai-provisioning/specs/venue-lambdalabs/`
- `codecraftai-credentials/specs/lambdalabs-credentials/`

---

## Testing Strategy

Example-based tests cover construction, key/filesystem idempotent
register, launch+terminate happy paths, and HTTP-error reclassification.

Property-based tests (hypothesis) are **required** for:
1. **Paging cursor traversal** across `list_*` endpoints.
2. **URL composition** — per-segment percent-encoding, empty/`None` rejection,
   deterministic output.
3. **Idempotent retry semantics** within and beyond the configured budget.
4. **`wait_until_running` waiter correctness** — termination on first
   `active` status in arbitrary monotonic mock streams; correct
   `TimeoutError` raise when the timeout exceeds the stream's length.

All unit tests use a mock transport; no live Lambda Labs account is needed.
