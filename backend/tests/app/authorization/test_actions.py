import json
from pathlib import Path

from app.core.authz import Action


class TestAction:
    def test_authorization_actions_equivalence(self):
        """
        Test to ensure that the AuthorizationAction enum in the TypeScript file
        matches the AuthorizationAction class in the Python file.
        """
        # Path to the TypeScript file

        ts_file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "frontend/src/types/authorization/rbac-actions.ts"
        )

        # Read the TypeScript file
        print(ts_file_path)
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

        # Extract the Python enum as a dictionary
        py_enum = {action.name: action.value for action in Action}

        # Compare the two dictionaries
        assert ts_enum == py_enum, (
            "Mismatch between TypeScript and"
            f"Python enums:\nTS: {json.dumps(ts_enum, indent=2)}\n"
            f"PY: {json.dumps(py_enum, indent=2)}"
        )
