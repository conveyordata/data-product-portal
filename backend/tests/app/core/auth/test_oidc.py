import pytest

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
            {"sub": "1", "name": "Prince", "email": "prince@example.com"}, "1", "email"
        )

        assert (identity.given_name, identity.family_name) == ("Prince", "")

    def test_from_claims__missing_name_uses_email_local_part(self):
        identity = OIDCIdentity.from_claims(
            {"sub": "1", "upn": "jan.peeters@example.com"}, "1", "upn"
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
            },
            "1",
            "email",
        )

        assert (identity.given_name, identity.family_name) == ("Anna", "van Dijk")

    def test_from_claims__last_comma_first_name_is_split_on_comma(self):
        identity = OIDCIdentity.from_claims(
            {"sub": "1", "name": "van Dijk, Anna", "email": "anna@contoso.com"},
            "1",
            "email",
        )

        assert (identity.given_name, identity.family_name) == ("Anna", "van Dijk")

    def test_from_claims__reads_only_the_configured_email_claim(self):
        identity = OIDCIdentity.from_claims(
            {
                "sub": "1",
                "name": "Anna",
                "email": "other@contoso.com",
                "preferred_username": "anna@contoso.com",
            },
            "1",
            "preferred_username",
        )

        assert identity.email == "anna@contoso.com"

    @pytest.mark.parametrize("value", [None, 42, "anna", "anna@"])
    def test_from_claims__configured_claim_without_email_is_rejected(self, value):
        with pytest.raises(ValueError, match="holds no email address"):
            OIDCIdentity.from_claims(
                {
                    "sub": "1",
                    "name": "Anna",
                    "preferred_username": value,
                    "upn": "anna@contoso.com",
                },
                "1",
                "preferred_username",
            )
