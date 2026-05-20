"""
    .. module:: pagingsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the transparent cursor-paging helper
                   shared by every Lambda Labs ``list_*`` api-group method.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Callable, List, Optional


# Lambda Labs v1 list endpoints return the full result in a single 'data'
# array.  Newer endpoints may add a 'next_cursor' field; this helper follows
# it transparently and degrades to a single page when it is absent.
DEFAULT_CURSOR_FIELD = "next_cursor"


def collect_all_pages(*, fetch_page: Callable[[Optional[str]], Any],
                      cursor_field: str = DEFAULT_CURSOR_FIELD) -> List[Any]:
    """
        Collect every item across a cursor-paginated Lambda Labs endpoint.

        ``fetch_page`` is invoked with the current cursor token (``None`` on
        the first call) and must return a two-tuple ``(items, next_cursor)``.
        Traversal continues until ``next_cursor`` is ``None`` or empty.

        :param fetch_page: Callable returning ``(items, next_cursor)``.
        :param cursor_field: Name of the cursor field (documentation only;
            ``fetch_page`` is responsible for reading it).

        :returns: The flattened list of items across every page.
    """
    # `cursor_field` is accepted so callers and tests can document which
    # field name the endpoint uses; the actual read happens in fetch_page.
    _ = cursor_field

    collected: List[Any] = []
    cursor: Optional[str] = None

    while True:
        page_items, next_cursor = fetch_page(cursor)
        for item in page_items:
            collected.append(item)

        if next_cursor is None:
            break
        if len(next_cursor) == 0:
            break

        cursor = next_cursor

    rtnval = collected
    return rtnval
