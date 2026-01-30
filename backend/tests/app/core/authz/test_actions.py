from app.core.authz.actions import AuthorizationAction


class TestActions:
    def test_str(self):
        assert str(AuthorizationAction.OUTPUT_PORT__DELETE) == "404"
