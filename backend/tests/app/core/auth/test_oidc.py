from app.core.auth.oidc import OIDCIdentity


class TestOIDCIdentity:
    def test_oidc_identity__given_name_claim_is_kept(self):
        identity = OIDCIdentity(
            sub="1",
            name="Bob Bobby",
            given_name="Bob",
            family_name="Bobby",
            email="bob@example.com",
        )

        assert identity.given_name == "Bob"

    def test_oidc_identity__missing_given_name_falls_back_to_name(self):
        identity = OIDCIdentity(
            sub="1",
            name="Bob",
            family_name="Bobby",
            email="bob@example.com",
        )

        assert identity.given_name == "Bob"
