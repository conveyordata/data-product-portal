from sqlalchemy import func, select

from app.configuration.platform_service_configurations.model import (
    PlatformServiceConfiguration,
)
from app.configuration.platforms.platform_services.model import PlatformService
from app.configuration.platforms.platform_services.service import (
    PlatformServiceService,
)
from app.plugins.registry import plugin_registry


def _ensure(session) -> None:
    PlatformServiceService(session).ensure_for_plugins(plugin_registry.discovered())
    session.commit()  # noqa: allow-commit


def _service(session, key: str) -> PlatformService:
    return session.scalars(
        select(PlatformService).where(func.lower(PlatformService.name) == key)
    ).one()


def _options(session, service: PlatformService) -> str:
    return session.scalars(
        select(PlatformServiceConfiguration.config).filter_by(service_id=service.id)
    ).one()


def test_ensure_for_plugins__adds_a_service_for_every_plugin_with_a_form(session):
    _ensure(session)

    for plugin in plugin_registry.discovered():
        metadata = plugin.get_platform_metadata()
        if metadata.result_string_template is None:
            continue
        service = _service(session, metadata.platform_key)
        assert service.platform.name == (
            metadata.parent_platform or metadata.platform_key
        )
        assert service.result_string_template == metadata.result_string_template
        assert _options(session, service) == "[]"


def test_ensure_for_plugins__updates_the_templates_of_an_existing_service(session):
    _ensure(session)
    _service(session, "s3").result_string_template = "old"
    session.commit()  # noqa: allow-commit

    _ensure(session)

    assert _service(session, "s3").result_string_template == "{bucket}/{suffix}/{path}"


def test_ensure_for_plugins__keeps_the_options_an_admin_filled_in(session):
    _ensure(session)
    s3 = _service(session, "s3")
    session.execute(
        PlatformServiceConfiguration.__table__.update()
        .where(PlatformServiceConfiguration.service_id == s3.id)
        .values(config='["datalake"]')
    )
    session.commit()  # noqa: allow-commit

    _ensure(session)

    assert _options(session, s3) == '["datalake"]'
