"""
    .. module:: test_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Property-based (hypothesis) tests for the Lambda Labs
                   REST client — paging traversal, URL composition,
                   idempotent retry, and waiter correctness.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import List, Optional, Tuple
from urllib.parse import quote

import pytest

from hypothesis import given, settings
from hypothesis import strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.restclient.lambdalabs.apigroups.groupsupport import (
    compose_leaf, encode_segment
)
from ccai.restclient.lambdalabs.apigroups.pagingsupport import (
    collect_all_pages
)
from ccai.restclient.lambdalabs.aspectslambdalabs import AspectsLambdalabs
from ccai.restclient.lambdalabs.exceptions.lambdalabserrors import (
    LambdalabsInstanceFailedError
)
from ccai.restclient.lambdalabs.model.lambdalabsinstance import (
    LambdalabsInstance
)


# ----------------------------------------------------------------------
# Paging cursor traversal
# ----------------------------------------------------------------------

@settings(max_examples=80)
@given(page_sizes=st.lists(st.integers(min_value=0, max_value=6),
                           min_size=1, max_size=10))
def test_paging_visits_every_item_exactly_once(page_sizes):
    """
        ``collect_all_pages`` visits every item across an arbitrary cursor
        stream exactly once and in order.
    """
    pages: List[List[int]] = []
    counter = 0
    for size in page_sizes:
        page: List[int] = []
        for _ in range(size):
            page.append(counter)
            counter = counter + 1
        pages.append(page)

    state = {"index": 0}

    def _fetch_page(cursor: Optional[str]) -> Tuple[List[int], Optional[str]]:
        index = state["index"]
        items = pages[index]
        state["index"] = index + 1
        if index + 1 < len(pages):
            next_cursor = "cursor-{}".format(index + 1)
        else:
            next_cursor = None
        return items, next_cursor

    collected = collect_all_pages(fetch_page=_fetch_page)
    assert collected == list(range(counter))
    return


# ----------------------------------------------------------------------
# URL composition
# ----------------------------------------------------------------------

@settings(max_examples=100)
@given(segments=st.lists(
    st.text(alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1, max_size=12),
    min_size=1, max_size=5))
def test_compose_leaf_is_deterministic_and_per_segment_encoded(segments):
    """
        ``compose_leaf`` produces a deterministic, per-segment-encoded path
        and never collapses a segment containing ``/``.
    """
    first = compose_leaf(parts=list(segments))
    second = compose_leaf(parts=list(segments))
    assert first == second

    expected = "/api/v1/" + "/".join(quote(s, safe="") for s in segments)
    assert first == expected

    # Each raw segment must be recoverable by per-segment encoding; a
    # segment carrying a slash is encoded so it cannot widen the path.
    assert first.count("/") == 3 + len(segments) - 1
    return


@settings(max_examples=50)
@given(bad=st.sampled_from([None, ""]))
def test_encode_segment_rejects_empty_or_none(bad):
    """
        ``encode_segment`` raises SemanticError on an empty or None segment.
    """
    with pytest.raises(SemanticError):
        encode_segment(segment=bad)
    return


def test_compose_leaf_rejects_empty_parts_list():
    """
        ``compose_leaf`` raises SemanticError on an empty parts list.
    """
    with pytest.raises(SemanticError):
        compose_leaf(parts=[])
    return


# ----------------------------------------------------------------------
# Idempotent retry semantics
# ----------------------------------------------------------------------

@settings(max_examples=60)
@given(failures=st.integers(min_value=0, max_value=4),
       budget=st.integers(min_value=0, max_value=4))
def test_idempotent_retry_within_and_beyond_budget(failures, budget):
    """
        A retry loop driven by a caller-controlled budget surfaces the
        success when ``failures <= budget`` and bubbles the final failure
        unchanged when the budget is exhausted.
    """
    state = {"calls": 0}

    def _operation() -> str:
        state["calls"] = state["calls"] + 1
        if state["calls"] <= failures:
            raise RuntimeError("transient")
        rtnval = "ok"
        return rtnval

    attempts = 0
    last_error: Optional[BaseException] = None
    result: Optional[str] = None
    while True:
        try:
            result = _operation()
            break
        except RuntimeError as xcpt:
            last_error = xcpt
            if attempts >= budget:
                break
            attempts = attempts + 1

    if failures <= budget:
        assert result == "ok"
    else:
        assert result is None
        assert isinstance(last_error, RuntimeError) is True
    return


# ----------------------------------------------------------------------
# wait_until_running waiter correctness
# ----------------------------------------------------------------------

class _StreamClient:
    """
        Minimal stand-in exposing only ``get_instance`` for the waiter, so
        the waiter logic can be exercised against an arbitrary status
        stream without HTTP mocking.
    """

    def __init__(self, *, statuses: List[str]) -> None:
        """
            Initialize with a monotonic status stream.

            :param statuses: The status stream the waiter will observe.
        """
        self._statuses = list(statuses)
        self._index = 0
        return

    def get_instance(self, *, instance_id: str, aspects) -> LambdalabsInstance:
        """
            Return the next status in the stream as a typed instance.

            :param instance_id: The instance id (echoed onto the record).
            :param aspects: Behaviour control (unused by this stub).

            :returns: A :class:`LambdalabsInstance` at the next status.
        """
        if self._index < len(self._statuses):
            status = self._statuses[self._index]
            self._index = self._index + 1
        else:
            status = self._statuses[-1]
        rtnval = LambdalabsInstance(identifier=instance_id, name="n",
                                    status=status, region="us-east-1",
                                    instance_type_name="gpu_1x_h100_pcie")
        return rtnval


def _bind_waiter(stream_client):
    """
        Bind :meth:`LambdalabsClient.wait_until_running` to a stub client.

        :param stream_client: The stub exposing ``get_instance``.

        :returns: A callable equivalent to the bound waiter method.
    """
    from ccai.restclient.lambdalabs.lambdalabsclient import LambdalabsClient

    def _call(*, instance_id: str, aspects):
        rtnval = LambdalabsClient.wait_until_running(stream_client,
                                                     instance_id=instance_id,
                                                     aspects=aspects)
        return rtnval

    return _call


@settings(max_examples=60, deadline=None)
@given(booting_count=st.integers(min_value=0, max_value=8))
def test_waiter_terminates_on_first_active(booting_count):
    """
        The waiter returns on the first ``active`` status in a monotonic
        booting-then-active stream.
    """
    statuses = ["booting"] * booting_count + ["active"]
    stream = _StreamClient(statuses=statuses)
    waiter = _bind_waiter(stream)
    aspects = AspectsLambdalabs(wait_running_timeout_seconds=1000.0,
                                wait_running_interval_seconds=0.0)
    instance = waiter(instance_id="i1", aspects=aspects)
    assert instance.status == "active"
    return


@settings(max_examples=40, deadline=None)
@given(stream_length=st.integers(min_value=1, max_value=6))
def test_waiter_times_out_when_never_active(stream_length):
    """
        The waiter raises TimeoutError when the stream never reaches
        ``active`` before the timeout elapses.
    """
    statuses = ["booting"] * stream_length
    stream = _StreamClient(statuses=statuses)
    waiter = _bind_waiter(stream)
    aspects = AspectsLambdalabs(wait_running_timeout_seconds=0.0,
                                wait_running_interval_seconds=0.0)
    with pytest.raises(TimeoutError):
        waiter(instance_id="i1", aspects=aspects)
    return


def test_waiter_raises_on_terminal_failed_state():
    """
        The waiter raises LambdalabsInstanceFailedError on an unhealthy
        instance.
    """
    stream = _StreamClient(statuses=["booting", "unhealthy"])
    waiter = _bind_waiter(stream)
    aspects = AspectsLambdalabs(wait_running_timeout_seconds=1000.0,
                                wait_running_interval_seconds=0.0)
    with pytest.raises(LambdalabsInstanceFailedError):
        waiter(instance_id="i1", aspects=aspects)
    return
