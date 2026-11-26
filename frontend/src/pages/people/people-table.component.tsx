import { TeamOutlined } from '@ant-design/icons';
import { Col, Row, Typography } from 'antd';
import { parseAsString, useQueryState } from 'nuqs';
import { useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { EmptyState, hasFailed } from '@/components/empty-state/empty-state.component.tsx';
import { IdentitySelector } from '@/components/identity-selector/identity-selector.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useCreateGlobalRoleAssignmentMutation,
    useDecideGlobalRoleAssignmentMutation,
    useDeleteGlobalRoleAssignmentMutation,
    useListGlobalRoleAssignmentsQuery,
    useModifyGlobalRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { useSetCanBecomeAdminMutation } from '@/store/api/services/generated/usersApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DecisionStatus, type GlobalRoleAssignment, Prototype, Scope } from '@/types/roles';
import { dispatchMessage } from '@/utils/feedback.ts';
import styles from './people-table.module.scss';
import { getPeopleTableColumns } from './people-table-columns';

export function PeoplePage() {
    const { t } = useTranslation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <TeamOutlined /> {t('People')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);

    const rolesQuery = useGetRolesQuery(Scope.GLOBAL);
    const assignmentsQuery = useListGlobalRoleAssignmentsQuery({});
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_USER });
    const { data: deleteAccess } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__DELETE_USER });
    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));
    const [createGlobalRoleAssignment, { isLoading: isCreating }] = useCreateGlobalRoleAssignmentMutation();
    const [updateGlobalRoleAssignment, { isLoading: isUpdating }] = useModifyGlobalRoleAssignmentMutation();
    const [decideGlobalRoleAssignment, { isLoading: isDeciding }] = useDecideGlobalRoleAssignmentMutation();
    const [deleteGlobalRoleAssignment, { isLoading: isDeleting }] = useDeleteGlobalRoleAssignmentMutation();
    const [canBecomeAdmin, { isLoading: isChangingAdmin }] = useSetCanBecomeAdminMutation();
    const isSaving =
        isCreating ||
        isUpdating ||
        isDeciding ||
        isDeleting ||
        isChangingAdmin ||
        rolesQuery.isFetching ||
        assignmentsQuery.isFetching;

    const onChangeGlobalRole = useCallback(
        async (identity_id: string, value: string, original: GlobalRoleAssignment | null) => {
            if (original?.role.id === value && original.decision === DecisionStatus.Approved) return;
            let success = t('Global role successfully assigned');
            let failure = t('Could not assign global role');
            try {
                if (original && !value) {
                    success = t('Global role assignment successfully reset');
                    failure = t('Could not reset global role assignment');
                    await deleteGlobalRoleAssignment(original.id).unwrap();
                } else if (original && value && original.decision !== DecisionStatus.Denied) {
                    success = t('Global role assignment successfully changed');
                    failure = t('Could not change global role assignment');
                    if (original.role.id !== value) {
                        await updateGlobalRoleAssignment({
                            id: original.id,
                            modifyGlobalRoleAssignment: { role_id: value },
                        }).unwrap();
                    }
                    if (original.decision === DecisionStatus.Pending) {
                        failure = t('Could not confirm the role assignment. Select the role again to retry.');
                        await decideGlobalRoleAssignment({
                            id: original.id,
                            decideGlobalRoleAssignment: { decision: DecisionStatus.Approved },
                        }).unwrap();
                    }
                } else if (value) {
                    if (original) {
                        await deleteGlobalRoleAssignment(original.id).unwrap();
                    }
                    const created = await createGlobalRoleAssignment({ identity_id, role_id: value }).unwrap();
                    failure = t('Could not confirm the role assignment. Select the role again to retry.');
                    await decideGlobalRoleAssignment({
                        id: created.id,
                        decideGlobalRoleAssignment: { decision: DecisionStatus.Approved },
                    }).unwrap();
                } else {
                    return;
                }
                dispatchMessage({ content: success, type: 'success' });
            } catch {
                dispatchMessage({ content: failure, type: 'error' });
            }
        },
        [
            t,
            deleteGlobalRoleAssignment,
            updateGlobalRoleAssignment,
            createGlobalRoleAssignment,
            decideGlobalRoleAssignment,
        ],
    );

    const loadFailed = hasFailed(rolesQuery) || hasFailed(assignmentsQuery);
    return (
        <Row gutter={[16, 16]}>
            <Col span={24}>
                <Typography.Title level={3}>{t('People')}</Typography.Title>
            </Col>
            <Col span={24}>
                {loadFailed ? (
                    <EmptyState
                        icon={<TeamOutlined />}
                        title={t('No roles available')}
                        subject={t('role assignments')}
                        error
                        onRetry={() => {
                            rolesQuery.refetch();
                            assignmentsQuery.refetch();
                        }}
                    />
                ) : (
                    <div data-testid="people-table">
                        <IdentitySelector
                            search={{ value: searchTerm, onChange: setSearchTerm, span: 10 }}
                            columns={(identities, identitiesDisabled) =>
                                getPeopleTableColumns({
                                    t,
                                    identities,
                                    assignments: assignmentsQuery.currentData?.role_assignments ?? [],
                                    canAssignRole: access?.allowed ?? false,
                                    canDeleteRole: deleteAccess?.allowed ?? false,
                                    allRoles: (rolesQuery.currentData?.roles ?? []).filter(
                                        (role) => role.prototype !== Prototype.ADMIN,
                                    ),
                                    onChange: onChangeGlobalRole,
                                    isSaving: isSaving || identitiesDisabled,
                                    changeCheckbox: async (user_id, can_become_admin) => {
                                        try {
                                            await canBecomeAdmin({ user_id, can_become_admin }).unwrap();
                                        } catch {
                                            dispatchMessage({
                                                content: t('Could not change admin eligibility'),
                                                type: 'error',
                                            });
                                        }
                                    },
                                })
                            }
                            tableProps={{
                                tableLayout: undefined,
                                scroll: undefined,
                                rowClassName: styles.row,
                                rowHoverable: true,
                            }}
                        />
                    </div>
                )}
            </Col>
        </Row>
    );
}
