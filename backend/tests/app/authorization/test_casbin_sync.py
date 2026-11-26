from collections.abc import Iterable
from datetime import timedelta

from casbin_sqlalchemy_adapter import CasbinRule
from sqlalchemy import select

from app.authorization.casbin_sync import CasbinSync
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.model import Role
from app.authorization.roles.schema import Prototype, Scope
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import CasbinPolicies
from app.core.authz.rules import DATA_PRODUCT_READER_ROLE, OUTPUT_PORT_READER_ROLE
from app.data_products.model import DataProductVisibility
from app.data_products.output_ports.model import OutputPortAccessFunction
from app.shared.model import utcnow
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)
from tests.factories.group import GroupFactory, GroupMembershipFactory


class TestCasbinSync:
    def test_rebuild__writes_every_rule_kind(self, policies: CasbinPolicies, session):
        resource_role = RoleFactory(
            scope="data_product",
            permissions=[
                AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
                AuthorizationAction.DATA_PRODUCT__DELETE,
            ],
        )
        global_role = RoleFactory(
            scope="global", permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        admin = UserFactory(admin_expiry=utcnow() + timedelta(days=1))
        GlobalRoleAssignmentFactory(identity_id=admin.id, role_id=ADMIN_UUID)
        global_user = UserFactory()
        GlobalRoleAssignmentFactory(identity_id=global_user.id, role_id=global_role.id)

        discoverable = DataProductFactory(visibility=DataProductVisibility.DISCOVERABLE)
        hidden = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
        member = UserFactory()
        DataProductRoleAssignmentFactory(
            identity_id=member.id,
            data_product_id=discoverable.id,
            role_id=resource_role.id,
        )
        DataProductRoleAssignmentFactory(
            identity_id=UserFactory().id,
            data_product_id=hidden.id,
            role_id=resource_role.id,
            decision=DecisionStatus.PENDING,
        )

        OutputPortFactory(
            data_product=hidden, access_function=OutputPortAccessFunction.PRIVATE
        )
        open_output_port = OutputPortFactory(data_product=hidden)
        output_port_user = UserFactory()
        DatasetRoleAssignmentFactory(
            output_port=open_output_port,
            user_id=output_port_user.id,
            role_id=resource_role.id,
        )
        DatasetRoleAssignmentFactory(
            output_port=open_output_port,
            user_id=UserFactory().id,
            role_id=resource_role.id,
            decision=DecisionStatus.PENDING,
        )

        group = GroupFactory()
        group_member = UserFactory()
        GroupMembershipFactory(group=group, member=group_member)

        policies.assign_resource_role(user_id="x", role_id="y", resource_id="z")
        policies.assign_domain_role(user_id="x", role_id="y", domain_id="z")

        CasbinSync(session).rebuild()

        built_in_roles = {
            (role.scope, role.prototype): role
            for role in session.scalars(
                select(Role).where(Role.prototype != Prototype.CUSTOM)
            )
        }
        assert set(built_in_roles) == {
            (Scope.DATA_PRODUCT, Prototype.OWNER),
            (Scope.DATASET, Prototype.OWNER),
            (Scope.GLOBAL, Prototype.EVERYONE),
            (Scope.GLOBAL, Prototype.ADMIN),
        }
        data_product_owner = built_in_roles[(Scope.DATA_PRODUCT, Prototype.OWNER)]
        output_port_owner = built_in_roles[(Scope.DATASET, Prototype.OWNER)]
        everyone = built_in_roles[(Scope.GLOBAL, Prototype.EVERYONE)]
        admin_role = built_in_roles[(Scope.GLOBAL, Prototype.ADMIN)]
        resource_role_id = str(resource_role.id)
        assert _rules(session) == {
            *_policies(data_product_owner.id, data_product_owner.permissions),
            *_policies(output_port_owner.id, output_port_owner.permissions),
            *_policies("*", everyone.permissions),
            *_policies(admin_role.id, admin_role.permissions),
            *_policies(resource_role.id, resource_role.permissions),
            *_policies(global_role.id, global_role.permissions),
            *_policies(
                DATA_PRODUCT_READER_ROLE,
                [AuthorizationAction.HIDDEN__DATA_PRODUCT__READ],
            ),
            *_policies(
                OUTPUT_PORT_READER_ROLE, [AuthorizationAction.HIDDEN__OUTPUT_PORT__READ]
            ),
            ("g3", str(admin.id), "*", None),
            ("g3", str(global_user.id), str(global_role.id), None),
            ("g", "*", DATA_PRODUCT_READER_ROLE, str(discoverable.id)),
            ("g", str(member.id), resource_role_id, str(discoverable.id)),
            ("g", "*", OUTPUT_PORT_READER_ROLE, str(open_output_port.id)),
            (
                "g",
                str(output_port_user.id),
                resource_role_id,
                str(open_output_port.id),
            ),
            ("g", str(group_member.id), str(group.id), "*"),
            ("g3", str(group_member.id), str(group.id), None),
        }

    def test_rebuild__writes_admin_rules(self, policies: CasbinPolicies, session):
        temporary = UserFactory(admin_expiry=utcnow() + timedelta(days=1))
        expired = UserFactory(admin_expiry=utcnow() - timedelta(days=1))
        permanent = UserFactory()
        GlobalRoleAssignmentFactory(identity_id=permanent.id, role_id=ADMIN_UUID)
        requested = UserFactory()
        GlobalRoleAssignmentFactory(
            identity_id=requested.id,
            role_id=ADMIN_UUID,
            decision=DecisionStatus.PENDING,
        )
        denied = UserFactory()
        GlobalRoleAssignmentFactory(
            identity_id=denied.id, role_id=ADMIN_UUID, decision=DecisionStatus.DENIED
        )
        admin_group = GroupFactory()
        GlobalRoleAssignmentFactory(identity_id=admin_group.id, role_id=ADMIN_UUID)
        group_member = UserFactory()
        GroupMembershipFactory(group=admin_group, member=group_member)

        CasbinSync(session).rebuild()

        identities = {
            str(identity.id)
            for identity in (
                temporary,
                expired,
                permanent,
                requested,
                denied,
                admin_group,
                group_member,
            )
        }
        assert {
            rule
            for rule in _rules(session)
            if rule[0] == "g3" and rule[1] in identities
        } == {
            ("g3", str(temporary.id), "*", None),
            ("g3", str(permanent.id), "*", None),
            ("g3", str(admin_group.id), "*", None),
            ("g3", str(group_member.id), str(admin_group.id), None),
        }
        assert policies.allows(
            sub=str(group_member.id),
            dom="*",
            obj="*",
            act=AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION,
        )

    def test_rebuild__keeps_discoverable_data_products(self, session):
        existing = len(session.query(CasbinRule).all())

        for i in range(5):
            DataProductFactory(visibility=DataProductVisibility.DISCOVERABLE)
            DataProductFactory(visibility=DataProductVisibility.HIDDEN)

        assert len(session.query(CasbinRule).all()) == 5 + existing, (
            "factories write one reader rule per Discoverable Data Product"
        )

        CasbinSync(session).rebuild()

        assert len(session.query(CasbinRule).all()) == 5 + existing, (
            "rebuild keeps exactly those reader rules"
        )

    def test_rebuild__syncs_group_data_product_access(
        self, policies: CasbinPolicies, session
    ):
        user = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)

        data_product = DataProductFactory()
        role = RoleFactory(
            scope="data_product",
            permissions=[AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            identity=group,
            data_product=data_product,
            role=role,
        )

        CasbinSync(session).rebuild()
        assert policies.allows(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        )
        assert policies.has_resource_role(
            user_id=str(user.id),
            role_id=str(group.id),
            resource_id="*",
        )
        assert not policies.has_resource_role(
            user_id=str(user.id),
            role_id=str(group.id),
            resource_id=str(data_product.id),
        )

    def test_rebuild__syncs_group_global_access(
        self, policies: CasbinPolicies, session
    ):
        user = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)

        action = AuthorizationAction.DATA_PRODUCT__DELETE
        role = RoleFactory(
            scope="global",
            permissions=[action],
        )
        GlobalRoleAssignmentFactory(
            identity=group,
            role=role,
        )

        CasbinSync(session).rebuild()

        assert policies.allows(
            sub=str(user.id),
            dom="*",
            obj="*",
            act=action,
        )

    def test_rebuild__revokes_access_after_membership_removal(
        self, policies: CasbinPolicies, session
    ):
        """Relies on `build_role_links()` in `CasbinPolicies.replace_all()`."""
        user = UserFactory()
        group = GroupFactory()
        membership = GroupMembershipFactory(group=group, member=user)

        data_product = DataProductFactory()
        role = RoleFactory(
            scope="data_product",
            permissions=[AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            identity=group,
            data_product=data_product,
            role=role,
        )

        CasbinSync(session).rebuild()

        assert policies.allows(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        )

        session.delete(membership)
        session.flush()
        CasbinSync(session).rebuild()

        assert not policies.allows(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        )


def _rules(session) -> set[tuple[str | None, ...]]:
    return {
        (rule.ptype, rule.v0, rule.v1, rule.v2)
        for rule in session.scalars(select(CasbinRule))
    }


def _policies(
    subject: object, actions: Iterable[AuthorizationAction]
) -> set[tuple[str | None, ...]]:
    return {("p", str(subject), str(action), None) for action in actions}
