=========================================
Automation Mojo Interop - Lambda Labs
=========================================

The ``automojo-interop-lambdalabs`` package is the venue-specific REST client for Lambda
Labs, a GPU-focused cloud whose API surface is one of the smallest and cleanest in the
AI-cloud landscape. The provider exposes a traditional IaaS shape — ``instances``,
``ssh-keys``, ``file-systems``, and ``1-click-clusters`` — with no Kubernetes or
workload-shaped surface, which makes Lambda Labs the natural first AI-cloud venue to land
end-to-end in ``automojo-provisioning``.

Highlights
==========

- ``LambdalabsClient`` — a ``RestClientBase`` subclass that authenticates against ``cloud.lambdalabs.com``.
- Instance lifecycle — enumerate instance types and regions, launch and terminate instances with attached SSH keys and optional shared file systems, and report status during the wait-for-running stage of an ``apply``.
- 1-click clusters — provision and reuse multi-node clusters for distributed training jobs.
- Neutral provisioning model — results map onto the ``CloudInstance`` + ``CloudSharedFilesystem`` + ``CloudAcceleratorSpec`` model defined in ``automojo-provisioning``.
- Aspects-driven transport — every behaviour-bearing call accepts ``aspects: AspectsRest = DEFAULT_LAMBDALABS_ASPECTS``; credentials enter as typed ``LambdalabsApiKeyCredential`` instances from ``automojo-credentials``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/automojo/interop/lambdalabs/`` - Package source code.
- ``source/testroots/testbase/automojo/tests/interop/lambdalabs/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

.. code-block:: bash

   source .venv/bin/activate
   PYTHONPATH=source/packages:source/testroots/testbase python -m pytest source/testroots -q

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
