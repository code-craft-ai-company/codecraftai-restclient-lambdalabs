"""
    .. module:: groupsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains shared helpers used by the Lambda
                   Labs api-group classes — URL composition, status checks,
                   and JSON-payload extraction.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any, Dict, List
from urllib.parse import quote

from requests import Response

from automojo.errors.exceptions import SemanticError

from automojo.restclient.lambdalabs.exceptions.lambdalabserrors import (
    LambdalabsAuthenticationError, LambdalabsError,
    LambdalabsQuotaExceededError
)


# Lambda Labs versioned API base path.
API_V1_BASE = "/api/v1"


def encode_segment(*, segment: str) -> str:
    """
        Percent-encode a single path segment.

        The ``/`` character is treated as a reserved character and is
        therefore encoded so a single identifier can never silently expand
        the URL path.

        :param segment: The raw path segment.

        :returns: The percent-encoded segment.

        :raises: :class:`SemanticError` when the segment is ``None`` or
            empty.
    """
    if segment is None:
        raise SemanticError("URL path segment must be a non-empty string.")
    if len(segment) == 0:
        raise SemanticError("URL path segment must be a non-empty string.")

    rtnval = quote(segment, safe="")
    return rtnval


def compose_leaf(*, parts: List[str]) -> str:
    """
        Compose an API leaf path from the versioned base and per-segment
        percent-encoded parts.

        :param parts: The ordered path segments after the versioned base.

        :returns: The composed leaf path beginning with ``/``.

        :raises: :class:`SemanticError` when ``parts`` is ``None`` or empty,
            or when any segment is empty.
    """
    if parts is None:
        raise SemanticError("compose_leaf requires a non-None parts list.")
    if len(parts) == 0:
        raise SemanticError("compose_leaf requires at least one part.")

    encoded: List[str] = []
    for part in parts:
        encoded.append(encode_segment(segment=part))

    rtnval = API_V1_BASE + "/" + "/".join(encoded)
    return rtnval


def require_identifier(*, value: str, name: str) -> None:
    """
        Validate that an identifier argument is a non-empty string.

        :param value: The identifier value.
        :param name: The argument name, used in the error message.

        :returns: ``None``.

        :raises: :class:`SemanticError` when the identifier is ``None`` or
            empty.
    """
    if value is None:
        raise SemanticError("'{}' must be a non-empty string.".format(name))
    if len(value) == 0:
        raise SemanticError("'{}' must be a non-empty string.".format(name))
    return


def raise_for_status(*, response: Response, action: str) -> None:
    """
        Raise a descriptive Lambda Labs error for a non-2xx response.

        HTTP 401/403 reclassifies into :class:`LambdalabsAuthenticationError`.
        HTTP 400/403 carrying a quota/capacity error code reclassifies into
        :class:`LambdalabsQuotaExceededError`.  Every other non-2xx status
        reclassifies into :class:`LambdalabsError`.

        :param response: The :class:`Response` to inspect.
        :param action: A short description of the attempted action.

        :returns: ``None``.

        :raises: :class:`LambdalabsAuthenticationError`,
            :class:`LambdalabsQuotaExceededError`, :class:`LambdalabsError`.
    """
    status = response.status_code
    if 200 <= status < 300:
        return

    error_code = _error_code_of(response=response)

    err_msg_lines = ["Lambda Labs API call failed: {}.".format(action)]
    err_msg_lines.append("STATUS: {}".format(status))
    if error_code is not None:
        err_msg_lines.append("ERROR CODE: {}".format(error_code))
    err_msg_lines.append("RESPONSE:")
    err_msg_lines.append(response.text)
    err_msg = os.linesep.join(err_msg_lines)

    if status in (401, 403) and error_code != "global/quota-exceeded":
        raise LambdalabsAuthenticationError(err_msg)

    quota_codes = frozenset({
        "global/quota-exceeded", "instance-operations/launch/insufficient-capacity",
        "global/account-inactive",
    })
    if error_code in quota_codes:
        raise LambdalabsQuotaExceededError(err_msg)

    raise LambdalabsError(err_msg)


def _error_code_of(*, response: Response) -> Any:
    """
        Extract the Lambda Labs ``error.code`` field from a response body.

        :param response: The :class:`Response` to inspect.

        :returns: The error code string, or ``None`` when absent.
    """
    payload = safe_json(response=response)
    error_block = payload.get("error", None)
    if error_block is None:
        rtnval = None
        return rtnval
    if not isinstance(error_block, dict):
        rtnval = None
        return rtnval
    rtnval = error_block.get("code", None)
    return rtnval


def safe_json(*, response: Response) -> Dict[str, Any]:
    """
        Parse a response body as a JSON object, degrading to an empty dict.

        :param response: The :class:`Response` to parse.

        :returns: The decoded object, or an empty dict.
    """
    try:
        payload = response.json()
    except ValueError:
        rtnval: Dict[str, Any] = {}
        return rtnval

    if not isinstance(payload, dict):
        rtnval = {}
        return rtnval

    rtnval = payload
    return rtnval


def extract_data(*, response: Response, action: str) -> Any:
    """
        Extract the ``data`` envelope from a Lambda Labs API response.

        Lambda Labs wraps every successful response in a ``{"data": ...}``
        envelope.

        :param response: The :class:`Response` to parse.
        :param action: A short description of the attempted action.

        :returns: The contents of the ``data`` key.

        :raises: :class:`LambdalabsError` when the envelope is missing.
    """
    payload = safe_json(response=response)
    if "data" not in payload:
        err_msg_lines = [
            "Lambda Labs API response missing 'data' envelope: {}.".format(
                action
            )
        ]
        err_msg_lines.append("RESPONSE:")
        err_msg_lines.append(response.text)
        err_msg = os.linesep.join(err_msg_lines)
        raise LambdalabsError(err_msg)

    rtnval = payload["data"]
    return rtnval
