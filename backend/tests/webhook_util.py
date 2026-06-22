from unittest.mock import AsyncMock

import pytest


def assert_event_in_queue(expected_event_type: str, mock_webhook: AsyncMock) -> None:
    event_types_found = set()
    if not mock_webhook.await_args_list:
        assert pytest.fail("No events found in queue")
    for args_items in mock_webhook.await_args_list:
        event_type, payload = args_items.args
        event_types_found.add(event_type)
        if event_type == expected_event_type:
            return
    pytest.fail(
        f"Event {expected_event_type} not found in queue, found types: {event_types_found}"
    )


def assert_event_not_in_queue(
    expected_event_type: str, mock_webhook: AsyncMock
) -> None:
    event_types_found = set()
    if not mock_webhook.await_args_list:
        assert pytest.fail("No events found in queue")
    for args_items in mock_webhook.await_args_list:
        event_type, payload = args_items.args
        event_types_found.add(event_type)
        if event_type == expected_event_type:
            pytest.fail(
                f"Event {expected_event_type} found in queue, found types: {event_types_found}"
            )
