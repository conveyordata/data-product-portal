from app.authorization.role_assignments.enums import DecisionStatus
from app.core.logging.posthog_analytics import (
    consumption_metrics,
    provisioning_metrics,
)
from tests.factories import DataProductFactory, ExplorationFactory, InputPortFactory


def test_reports_total_approved_input_ports_split_by_type():
    exploration = ExplorationFactory()
    InputPortFactory(status=DecisionStatus.APPROVED)
    InputPortFactory(status=DecisionStatus.APPROVED)
    InputPortFactory(
        status=DecisionStatus.APPROVED,
        consuming_abstract_data_product=exploration,
    )
    InputPortFactory(status=DecisionStatus.PENDING)

    props = consumption_metrics()

    assert len(props) == 3
    assert props["total_approved_input_ports"] == 3
    assert props["approved_input_ports_data_products"] == 2
    assert props["approved_input_ports_explorations"] == 1


def test_reports_non_empty_finalizers_and_totals_by_type():
    DataProductFactory(finalizers=["cleanup"])
    DataProductFactory()
    ExplorationFactory(finalizers=["cleanup"])
    ExplorationFactory()

    props = provisioning_metrics()
    assert len(props) == 4

    assert props["provisioned_data_products"] == 1
    assert props["provisioned_explorations"] == 1
    assert props["total_data_products"] == 2
    assert props["total_explorations"] == 2
