import json
from pathlib import Path

from app.core.authz import Action


class TestAction:
    def test_authorization_actions_equivalence(self):
        """
        Test to ensure that the public AuthorizationAction enum in the TypeScript
        file matches the Python enum, while hidden 9xx actions stay backend-only.
        """
        # Path to the TypeScript file

        ts_file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "frontend/src/types/authorization/rbac-actions.ts"
        )

        # Read the TypeScript file
        with open(ts_file_path, "r") as ts_file:
            ts_content = ts_file.read()

        # Extract the TypeScript enum as a dictionary
        ts_enum = {}
        for line in ts_content.splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("//"):  # Ignore comments
                key, value = line.split("=")
                key = key.strip()
                value = value.strip().rstrip(",")
                ts_enum[key] = int(value)

        # Extract the Python enum as a dictionary, excluding backend-only 9xx actions
        py_enum = {
            action.name: action.value
            for action in Action
            if not 900 <= action.value < 1000
        }

        # Compare the two dictionaries
        assert ts_enum == py_enum, (
            "Mismatch between TypeScript and"
            f"Python enums:\nTS: {json.dumps(ts_enum, indent=2)}\n"
            f"PY: {json.dumps(py_enum, indent=2)}"
        )
        assert all(not 900 <= value < 1000 for value in ts_enum.values()), (
            "Frontend RBAC actions should not include backend-only 9xx actions:\n"
            f"TS: {json.dumps(ts_enum, indent=2)}"
        )
