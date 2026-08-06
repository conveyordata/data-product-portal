from fastapi import HTTPException, status

from app.core.errors.router_responses import process_errors_as_route_responses


def test_process_errors_as_route_responses__returns_example_for_single_status_error():
    responses = process_errors_as_route_responses(
        [
            HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Access modes are incompatible",
            )
        ]
    )

    assert responses == {
        409: {
            "description": "Access modes are incompatible",
            "content": {
                "application/json": {
                    "example": {"detail": "Access modes are incompatible"}
                }
            },
        }
    }


def test_process_errors_as_route_responses__groups_status_and_returns_examples_for_multiple_errors():
    responses = process_errors_as_route_responses(
        [
            HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error A"),
            HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error B"),
        ]
    )

    assert responses == {
        400: {
            "description": "Possible errors",
            "content": {
                "application/json": {
                    "examples": {
                        "error_a": {"value": {"detail": "Error A"}},
                        "error_b": {"value": {"detail": "Error B"}},
                    }
                }
            },
        }
    }
