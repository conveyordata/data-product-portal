from app.core.authz.actions import AuthorizationAction


class TestActions:

    def test_str(self):
        assert str(AuthorizationAction.DATASET__DELETE) == "404"
