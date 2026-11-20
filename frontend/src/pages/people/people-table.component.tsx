import { TeamOutlined } from '@ant-design/icons';
import { Col, Row, Typography } from 'antd';
import { parseAsString, useQueryState } from 'nuqs';
import { useEffect } from 'react';
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
import { getApiErrorDetail } from '@/store/common/errors.ts';
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
    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));
    const [createAssignment, { isLoading: isCreating }] = useCreateGlobalRoleAssignmentMutation();
    const [updateAssignment, { isLoading: isUpdating }] = useModifyGlobalRoleAssignmentMutation();
    const [decideAssignment, { isLoading: isDeciding }] = useDecideGlobalRoleAssignmentMutation();
    const [deleteAssignment, { isLoading: isDeleting }] = useDeleteGlobalRoleAssignmentMutation();
    const [canBecomeAdmin, { isLoading: isChangingAdmin }] = useSetCanBecomeAdminMutation();
    const isSaving =
        isCreating ||
        isUpdating ||
        isDeciding ||
        isDeleting ||
        isChangingAdmin ||
        rolesQuery.isFetching ||
        assignmentsQuery.isFetching;

    const onChangeGlobalRole = async (identity_id: string, value: string, original: GlobalRoleAssignment | null) => {
        if (original?.role.id === value && original.decision === DecisionStatus.Approved) return;
        let success = t('Global role successfully assigned');
        let failure = t('Could not assign global role');
        try {
            if (original && !value) {
                success = t('Global role assignment successfully reset');
                failure = t('Could not reset global role assignment');
                await deleteAssignment(original.id).unwrap();
            } else if (original && value && original.decision !== DecisionStatus.Denied) {
                success = t('Global role assignment successfully changed');
                failure = t('Could not change global role assignment');
                if (original.role.id !== value) {
                    await updateAssignment({
                        id: original.id,
                        modifyGlobalRoleAssignment: { role_id: value },
                    }).unwrap();
                }
                if (original.decision === DecisionStatus.Pending) {
                    failure = t('Could not confirm the role assignment. Select the role again to retry.');
                    await decideAssignment({
                        id: original.id,
                        decideGlobalRoleAssignment: { decision: DecisionStatus.Approved },
                    }).unwrap();
                }
            } else if (value) {
                if (original) {
                    try {
                        await deleteAssignment(original.id).unwrap();
                    } catch (error) {
                        if (getApiErrorDetail(error) === "You don't have permission to perform this action") {
                            failure = t(
                                "This identity has a previously denied role assignment. You don't have permission to replace it. Ask an administrator to assign the role.",
                            );
                        }
                        throw error;
                    }
                }
                const created = await createAssignment({ identity_id, role_id: value }).unwrap();
                failure = t('Could not confirm the role assignment. Select the role again to retry.');
                await decideAssignment({
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
    };

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
                            gap={16}
                            search={{ value: searchTerm, onChange: setSearchTerm, span: 10 }}
                            columns={(identities, identitiesDisabled) =>
                                getPeopleTableColumns({
                                    t,
                                    identities,
                                    assignments: assignmentsQuery.currentData?.role_assignments ?? [],
                                    canAssignRole: access?.allowed ?? false,
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
                                pagination: {
                                    showTotal: (total, range) =>
                                        t('Showing {{range0}}-{{range1}} of {{count}} identities', {
                                            range0: range[0],
                                            range1: range[1],
                                            count: total,
                                        }),
                                },
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
