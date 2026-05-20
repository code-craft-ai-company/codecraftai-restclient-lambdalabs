# Implementation Plan — Lambda Labs Client

## Package Skeleton

- [x] 1. Create `source/packages/automojo/restclient/lambdalabs/` package tree with `apigroups/`, `model/`, `specs/`, `exceptions/` subpackages.
- [x] 2. Add `aspectslambdalabs.py` defining `DEFAULT_LAMBDALABS_ASPECTS`.

## Client Core

- [x] 3. Implement `LambdalabsClient(RestClientBase)` with credential validation, Bearer-token auth, and HTTP-error reclassification.
- [x] 4. Implement URL composition helper (per-segment encoding, empty/`None` rejection).

## Data Model & Specs

- [x] 5. Implement model dataclasses for instance type, image, SSH key, filesystem, instance, cluster, termination result.
- [x] 6. Implement spec dataclasses for launch and cluster creation.

## API Groups

- [x] 7. Implement `InstanceTypesGroup.list(aspects)` with region capacity.
- [x] 8. Implement `ImagesGroup.list(aspects)`.
- [x] 9. Implement `SshKeysGroup.register / list / delete` with idempotency.
- [x] 10. Implement `FilesystemsGroup.create / list / delete` with idempotency.
- [x] 11. Implement `InstancesGroup.launch / get / list / terminate`.
- [x] 12. Implement `ClustersGroup.create / get / delete`.

## Waiters

- [x] 13. Implement `wait_until_running(instance_id, aspects)`.

## Paging

- [x] 14. Implement transparent cursor traversal for every `list_*` call.

## Tests — Example-Based

- [x] 15. Construction tests (valid/invalid credential).
- [x] 16. Idempotent register/create tests for SSH keys and filesystems.
- [x] 17. Launch + get + terminate happy-path tests.
- [x] 18. HTTP-error reclassification tests.

## Tests — Property-Based (hypothesis)

- [x] 19. Paging traversal totality across arbitrary cursor streams.
- [x] 20. URL composition determinism + per-segment encoding + rejection.
- [x] 21. Idempotent-retry equivalence within budget; bubble-through outside.
- [x] 22. `wait_until_running` terminal-state correctness against arbitrary monotonic mock streams.

## Integration

- [ ] 23. Smoke-test fixture for live Lambda Labs API (gated by env var), `multihost` tier.
