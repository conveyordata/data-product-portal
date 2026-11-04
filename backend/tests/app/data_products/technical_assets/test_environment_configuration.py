import uuid

import pytest
from sqlalchemy import select

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.model import DataProductEnvironment
from app.data_products.technical_assets.enums import TechnicalMapping
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    EnvironmentFactory,
    PlatformServiceFactory,
    RoleFactory,
    SizingTechnicalAssetConfigurationFactory,
    TagFactory,
    TechnicalAssetFactory,
    UserFactory,
)
from tests.fixtures.sizing_plugin.model import (
    NAME,
    SizingConfiguration,
)
from tests.fixtures.sizing_plugin.schema import (
    SizingTechnicalAssetConfiguration,
)
from tests.webhook_util import assert_event_in_queue, assert_event_not_in_queue

ENDPOINT = "/api/v2/data_products/{}/technical_assets"


@pytest.fixture
def dev():
    return EnvironmentFactory(name="dev", acronym="dev", is_global=False)


@pytest.fixture
def prd():
    return EnvironmentFactory(name="prd", acronym="prd", is_global=False)


@pytest.fixture
def data_product(dev, prd):
    return DataProductFactory(
        id=uuid.uuid4(),
        environments=[
            DataProductEnvironment(environment=dev),
            DataProductEnvironment(environment=prd),
        ],
    )


@pytest.fixture
def member(data_product):
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATA_PRODUCT,
        permissions=[
            Action.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
            Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
        ],
    )
    DataProductRoleAssignmentFactory(
        identity_id=user.id, role_id=role.id, data_product_id=data_product.id
    )
    return user


@pytest.fixture
def stored_asset(session, data_product, dev, prd):
    configuration = SizingTechnicalAssetConfigurationFactory()
    asset = TechnicalAssetFactory(owner=data_product, configuration=configuration)
    session.add_all(
        [
            SizingConfiguration(
                configuration_id=configuration.id,
                environment_id=dev.id,
                size="small",
                replicas=1,
                label="path-dev",
            ),
            SizingConfiguration(
                configuration_id=configuration.id,
                environment_id=prd.id,
                size="medium",
                replicas=2,
                label="path-prd",
            ),
        ]
    )
    session.commit()  # noqa: allow-commit
    return asset


def create_payload(data_product, **extra):
    return {
        "name": "asset",
        "description": "asset",
        "namespace": "asset-ns",
        "technical_mapping": "custom",
        "configuration": {"name": NAME, "path": "p"},
        "platform_id": str(PlatformServiceFactory().platform.id),
        "service_id": None,
        "tag_ids": [str(TagFactory().id)],
        **extra,
    }


def create(client, data_product, **extra):
    payload = create_payload(data_product, **extra)
    payload.pop("platform_id")
    payload.pop("service_id")
    return client.post(ENDPOINT.format(data_product.id), json=payload)


def put_values(client, asset, values):
    return client.put(
        f"{ENDPOINT.format(asset.owner_id)}/{asset.id}/environment_configuration",
        json={"environment_values": values},
    )


def validate_values(client, asset, values):
    return client.post(
        f"{ENDPOINT.format(asset.owner_id)}/{asset.id}/environment_configuration/validate",
        json={"environment_values": values},
    )


def get_asset(client, asset_id, data_product):
    return client.get(f"{ENDPOINT.format(data_product.id)}/{asset_id}")


def put_environments(client, data_product, *environments):
    return client.put(
        f"/api/v2/data_products/{data_product.id}",
        json={
            "name": data_product.name,
            "description": data_product.description,
            "namespace": data_product.namespace,
            "tag_ids": [],
            "type_id": str(data_product.type_id),
            "lifecycle_id": str(data_product.lifecycle_id),
            "domain_id": str(data_product.domain_id),
            "environment_ids": [str(e.id) for e in environments],
        },
    )


class TestCreateTechnicalAsset:
    def test_create_technical_asset__fills_defaults_per_environment(
        self, client, member, data_product, dev, prd
    ):
        response = create(client, data_product)

        assert response.status_code == 200, response.text
        values = get_asset(client, response.json()["id"], data_product).json()[
            "environment_values"
        ]
        assert values == {
            str(dev.id): {"size": "small", "replicas": 1, "label": "p-dev"},
            str(prd.id): {"size": "medium", "replicas": 1, "label": "p-prd"},
        }

    def test_create_technical_asset__keeps_provided_placeholder_value_literal(
        self, client, member, data_product, dev
    ):
        response = create(
            client, data_product, environment_values={str(dev.id): {"label": "{x}"}}
        )

        assert response.status_code == 200, response.text
        values = get_asset(client, response.json()["id"], data_product).json()[
            "environment_values"
        ]
        assert values[str(dev.id)]["label"] == "{x}"

    def test_create_technical_asset__rejects_unknown_placeholder_in_default(
        self, client, session, member, data_product
    ):
        unknown = EnvironmentFactory(name="unk", acronym="unk", is_global=False)
        session.add(
            DataProductEnvironment(
                data_product_id=data_product.id, environment_id=unknown.id
            )
        )
        session.flush()

        response = create(client, data_product)

        assert response.status_code == 422, response.text
        error = response.json()["detail"][0]
        assert error["environment_id"] == str(unknown.id)
        assert error["field"] == "label"

    def test_create_technical_asset__keeps_provided_values(
        self, client, member, data_product, dev, prd
    ):
        response = create(
            client, data_product, environment_values={str(prd.id): {"size": "large"}}
        )

        assert response.status_code == 200, response.text
        values = get_asset(client, response.json()["id"], data_product).json()[
            "environment_values"
        ]
        assert values[str(prd.id)] == {
            "size": "large",
            "replicas": 1,
            "label": "p-prd",
        }
        assert values[str(dev.id)] == {"size": "small", "replicas": 1, "label": "p-dev"}

    @pytest.mark.parametrize(
        ("values", "field", "message"),
        [
            ({"size": "large"}, "size", "Option is not allowed in this environment"),
            ({"size": "huge"}, "size", None),
            ({"colour": "red"}, "colour", "Extra inputs are not permitted"),
            ({"replicas": "many"}, "replicas", None),
            ({"replicas": 13}, "replicas", "Unlucky number of replicas"),
        ],
    )
    def test_create_technical_asset__rejects_invalid_cell(
        self, client, member, data_product, dev, values, field, message
    ):
        response = create(
            client, data_product, environment_values={str(dev.id): values}
        )

        assert response.status_code == 422, response.text
        error = response.json()["detail"][0]
        assert error["environment_id"] == str(dev.id)
        assert error["field"] == field
        if message:
            assert error["message"] == message

    def test_create_technical_asset__maps_model_level_error_to_no_field(
        self, client, member, data_product, dev
    ):
        response = create(
            client, data_product, environment_values={str(dev.id): {"replicas": 99}}
        )

        assert response.status_code == 422, response.text
        assert response.json()["detail"] == [
            {
                "environment_id": str(dev.id),
                "field": None,
                "message": "Value error, Too many replicas",
            }
        ]

    def test_create_technical_asset__passes_technical_mapping_to_plugin_hook(
        self, client, member, data_product, monkeypatch
    ):
        contexts = []
        monkeypatch.setattr(
            SizingTechnicalAssetConfiguration,
            "validate_environment_configuration",
            lambda self, values, context, db: contexts.append(context),
        )

        response = create(client, data_product)

        assert response.status_code == 200, response.text
        assert contexts[0].technical_asset.technical_mapping == TechnicalMapping.Custom

    def test_create_technical_asset__rejects_unknown_environment(
        self, client, member, data_product
    ):
        unknown = str(uuid.uuid4())

        response = create(
            client, data_product, environment_values={unknown: {"size": "small"}}
        )

        assert response.status_code == 422
        assert response.json()["detail"] == [
            {"environment_id": unknown, "field": None, "message": "Unknown environment"}
        ]

    def test_create_technical_asset__rejects_values_for_plugin_without_environment_fields(
        self, client, member, data_product, dev
    ):
        payload = create_payload(
            data_product, environment_values={str(dev.id): {"size": "small"}}
        )
        payload["configuration"] = {
            "name": "FakeTechnicalAssetConfiguration",
            "path": "p",
        }
        payload.pop("platform_id")
        payload.pop("service_id")

        response = client.post(ENDPOINT.format(data_product.id), json=payload)

        assert response.status_code == 400


class TestGetTechnicalAsset:
    def test_get_technical_asset__returns_values_per_environment(
        self, client, member, data_product, stored_asset, dev, prd
    ):
        response = get_asset(client, stored_asset.id, data_product)

        assert response.status_code == 200, response.text
        assert response.json()["environment_values"] == {
            str(dev.id): {"size": "small", "replicas": 1, "label": "path-dev"},
            str(prd.id): {"size": "medium", "replicas": 2, "label": "path-prd"},
        }

    def test_get_technical_asset__errors_on_missing_row(
        self, client, session, member, data_product, stored_asset, prd
    ):
        row = session.scalar(
            select(SizingConfiguration).where(
                SizingConfiguration.environment_id == prd.id
            )
        )
        session.delete(row)
        session.commit()  # noqa: allow-commit

        response = get_asset(client, stored_asset.id, data_product)

        assert response.status_code == 500
        assert f"environment {prd.name}" in response.json()["detail"]
        assert NAME in response.json()["detail"]

    def test_get_technical_asset__empty_for_plugin_without_environment_fields(
        self, client, member, data_product
    ):
        asset = TechnicalAssetFactory(owner=data_product)

        response = get_asset(client, asset.id, data_product)

        assert response.json()["environment_values"] == {}


class TestUpdateEnvironmentConfiguration:
    def test_update_technical_asset_environment_configuration__replaces_values(
        self, client, member, data_product, stored_asset, dev, prd, capture_events
    ):
        response = put_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "medium", "replicas": 3, "label": "l"},
                str(prd.id): {"size": "large", "replicas": 4, "label": "l"},
            },
        )

        assert response.status_code == 200, response.text
        assert response.json() == {"id": str(stored_asset.id)}
        assert get_asset(client, stored_asset.id, data_product).json()[
            "environment_values"
        ] == {
            str(dev.id): {"size": "medium", "replicas": 3, "label": "l"},
            str(prd.id): {"size": "large", "replicas": 4, "label": "l"},
        }
        assert_event_in_queue("technical_asset.event", capture_events)

    def test_update_technical_asset_environment_configuration__rejects_disabled_option(
        self, client, member, stored_asset, dev, prd, capture_events
    ):
        response = put_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "large", "replicas": 1, "label": "l"},
                str(prd.id): {"size": "medium", "replicas": 2, "label": "l"},
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "environment_id": str(dev.id),
                "field": "size",
                "message": "Option is not allowed in this environment",
            }
        ]
        assert_event_not_in_queue("technical_asset.event", capture_events)

    def test_update_technical_asset_environment_configuration__keeps_unchanged_disabled_option(
        self, client, session, member, data_product, stored_asset, dev, prd
    ):
        row = session.scalar(
            select(SizingConfiguration).where(
                SizingConfiguration.environment_id == dev.id
            )
        )
        row.size = "large"
        session.commit()  # noqa: allow-commit

        kept = put_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "large", "replicas": 5, "label": "l"},
                str(prd.id): {"size": "medium", "replicas": 2, "label": "l"},
            },
        )
        changed = put_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "huge", "replicas": 5, "label": "l"},
                str(prd.id): {"size": "medium", "replicas": 2, "label": "l"},
            },
        )

        assert kept.status_code == 200, kept.text
        assert changed.status_code == 422

    def test_update_technical_asset_environment_configuration__plugin_hook_sees_all_environments(
        self, client, member, stored_asset, dev, prd
    ):
        response = put_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "small", "replicas": 1, "label": "l"},
                str(prd.id): {"size": "medium", "replicas": 13, "label": "l"},
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "environment_id": str(prd.id),
                "field": "replicas",
                "message": "Unlucky number of replicas",
            }
        ]

    def test_update_technical_asset_environment_configuration__rejects_missing_environment(
        self, client, member, stored_asset, dev, prd
    ):
        response = put_values(
            client,
            stored_asset,
            {str(dev.id): {"size": "small", "replicas": 1, "label": "l"}},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "environment_id": str(prd.id),
                "field": None,
                "message": "Missing environment",
            }
        ]

    def test_update_technical_asset_environment_configuration__rejects_missing_field(
        self, client, member, stored_asset, dev, prd
    ):
        response = put_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "small"},
                str(prd.id): {"size": "medium", "replicas": 2, "label": "l"},
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["field"] == "replicas"

    def test_update_technical_asset_environment_configuration__rejects_plugin_without_environment_fields(
        self, client, member, data_product
    ):
        asset = TechnicalAssetFactory(owner=data_product)

        response = put_values(client, asset, {})

        assert response.status_code == 400

    def test_update_technical_asset_environment_configuration__requires_update_permission(
        self, client, stored_asset, dev, prd
    ):
        response = put_values(client, stored_asset, {})

        assert response.status_code == 403

    def test_update_technical_asset_environment_configuration__unknown_asset(
        self, client, member, data_product
    ):
        response = client.put(
            f"{ENDPOINT.format(data_product.id)}/{uuid.uuid4()}/environment_configuration",
            json={"environment_values": {}},
        )

        assert response.status_code in (403, 404)


class TestValidateEnvironmentConfiguration:
    def test_validate_technical_asset_environment_configuration__accepts_without_saving(
        self, client, member, data_product, stored_asset, dev, prd, capture_events
    ):
        before = get_asset(client, stored_asset.id, data_product).json()[
            "environment_values"
        ]

        response = validate_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "medium", "replicas": 3, "label": "l"},
                str(prd.id): {"size": "large", "replicas": 4, "label": "l"},
            },
        )

        assert response.status_code == 200, response.text
        assert (
            get_asset(client, stored_asset.id, data_product).json()[
                "environment_values"
            ]
            == before
        )
        assert_event_not_in_queue("technical_asset.event", capture_events)

    def test_validate_technical_asset_environment_configuration__rejects_disabled_option(
        self, client, member, stored_asset, dev, prd
    ):
        response = validate_values(
            client,
            stored_asset,
            {
                str(dev.id): {"size": "large", "replicas": 1, "label": "l"},
                str(prd.id): {"size": "medium", "replicas": 2, "label": "l"},
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "environment_id": str(dev.id),
                "field": "size",
                "message": "Option is not allowed in this environment",
            }
        ]

    def test_validate_technical_asset_environment_configuration__requires_update_permission(
        self, client, stored_asset
    ):
        response = validate_values(client, stored_asset, {})

        assert response.status_code == 403


class TestDataProductEnvironments:
    def test_update_data_product__copies_defaults_into_new_environment(
        self, client, admin, data_product, stored_asset, dev, prd
    ):
        sandbox = EnvironmentFactory(name="sbx", acronym="sbx", is_global=False)

        response = put_environments(client, data_product, dev, prd, sandbox)

        assert response.status_code == 200, response.text
        values = get_asset(client, stored_asset.id, data_product).json()[
            "environment_values"
        ]
        assert values[str(sandbox.id)] == {
            "size": "small",
            "replicas": 1,
            "label": "path-sbx",
        }
        assert values[str(prd.id)] == {
            "size": "medium",
            "replicas": 2,
            "label": "path-prd",
        }

    def test_update_data_product__rejects_unknown_placeholder_in_default(
        self, client, admin, data_product, stored_asset, dev, prd
    ):
        unknown = EnvironmentFactory(name="unk", acronym="unk", is_global=False)

        response = put_environments(client, data_product, dev, prd, unknown)

        assert response.status_code == 422, response.text
        error = response.json()["detail"][0]
        assert error["environment_id"] == str(unknown.id)
        assert error["field"] == "label"

    def test_update_data_product__rejects_invalid_default_for_new_environment(
        self, client, admin, data_product, stored_asset, dev, prd
    ):
        bad = EnvironmentFactory(name="bad", acronym="bad", is_global=False)

        response = put_environments(client, data_product, dev, prd, bad)

        assert response.status_code == 422, response.text
        error = response.json()["detail"][0]
        assert error["environment_id"] == str(bad.id)
        assert error["field"] == "replicas"
        assert NAME in error["message"]
        assert "bad" in error["message"]

    def test_update_data_product__runs_plugin_validation_for_new_environment(
        self, client, admin, data_product, stored_asset, dev, prd
    ):
        unlucky = EnvironmentFactory(name="ulk", acronym="ulk", is_global=False)

        response = put_environments(client, data_product, dev, prd, unlucky)

        assert response.status_code == 422, response.text
        assert response.json()["detail"] == [
            {
                "environment_id": str(unlucky.id),
                "field": "replicas",
                "message": "Unlucky number of replicas",
            }
        ]


class TestPluginForm:
    def test_get_plugin_form__exposes_environment_metadata(self, client, dev, prd):
        response = client.get(f"/api/v2/plugins/{NAME}/form")

        assert response.status_code == 200, response.text
        by_environment = {
            item["environment_id"]: {
                element["name"]: element for element in item["ui_metadata"]
            }
            for item in response.json()["environment_ui_metadata"]
        }
        prd_size = by_environment[str(prd.id)]["size"]["select"]
        dev_size = by_environment[str(dev.id)]["size"]["select"]
        assert prd_size["initial_value"] == "medium"
        assert dev_size["initial_value"] == "small"
        assert {o["value"]: o.get("disabled") for o in dev_size["options"]}["large"]
        assert not {o["value"]: o.get("disabled") for o in prd_size["options"]}["large"]

    def test_get_plugin_form__no_environment_metadata_without_environment_fields(
        self, client
    ):
        response = client.get("/api/v2/plugins/FakeTechnicalAssetConfiguration/form")

        assert response.json()["environment_ui_metadata"] == []

    @pytest.mark.parametrize(
        ("positions", "expected"),
        [
            ((None, None), ["dev", "prd"]),
            ((2, 1), ["prd", "dev"]),
            ((None, 1), ["prd", "dev"]),
        ],
    )
    def test_get_plugin_form__orders_environment_metadata(
        self, client, session, dev, prd, positions, expected
    ):
        dev.position, prd.position = positions
        session.commit()  # noqa: allow-commit
        names = {str(dev.id): "dev", str(prd.id): "prd"}

        response = client.get(f"/api/v2/plugins/{NAME}/form")

        assert [
            names[item["environment_id"]]
            for item in response.json()["environment_ui_metadata"]
        ] == expected

    def test_get_technical_asset__orders_environments_by_position(
        self, client, session, data_product, dev, prd, stored_asset
    ):
        dev.position, prd.position = 2, 1
        session.commit()  # noqa: allow-commit

        response = get_asset(client, stored_asset.id, data_product)

        assert [e["environment"]["name"] for e in response.json()["environments"]] == [
            "prd",
            "dev",
        ]
