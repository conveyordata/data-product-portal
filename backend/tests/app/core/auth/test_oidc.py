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

    def test_from_claims__single_word_name_has_empty_family_name(self):
        identity = OIDCIdentity.from_claims(
            {"sub": "1", "name": "Prince", "email": "prince@example.com"}
        )

        assert (identity.given_name, identity.family_name) == ("Prince", "")

    def test_from_claims__missing_name_uses_email_local_part(self):
        identity = OIDCIdentity.from_claims(
            {"sub": "1", "upn": "jan.peeters@example.com"}
        )

        assert (identity.name, identity.given_name, identity.email) == (
            "jan.peeters",
            "jan.peeters",
            "jan.peeters@example.com",
        )

    def test_from_claims__family_name_is_not_repeated_in_given_name(self):
        identity = OIDCIdentity.from_claims(
            {
                "sub": "1",
                "name": "Anna van Dijk",
                "family_name": "van Dijk",
                "email": "anna@contoso.com",
            }
        )

        assert (identity.given_name, identity.family_name) == ("Anna", "van Dijk")

    def test_from_claims__non_string_email_claims_are_skipped(self):
        identity = OIDCIdentity.from_claims(
            {
                "sub": "1",
                "name": "Anna",
                "email": 42,
                "upn": "anna@contoso.com",
            }
        )

        assert identity.email == "anna@contoso.com"

    def test_from_claims__invalid_email_candidate_falls_through_to_upn(self):
        identity = OIDCIdentity.from_claims(
            {
                "sub": "1",
                "name": "Anna",
                "preferred_username": "anna@",
                "upn": "anna@contoso.com",
            }
        )

        assert identity.email == "anna@contoso.com"
