import { TeamOutlined } from '@ant-design/icons';
import { Table } from 'antd';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import SearchPage from '@/components/search-page/search-page.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type GlobalRoleAssignmentResponse,
    useCreateGlobalRoleAssignmentMutation,
    useDecideGlobalRoleAssignmentMutation,
    useDeleteGlobalRoleAssignmentMutation,
    useModifyGlobalRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi.ts';
import {
    type UsersGet,
    useGetUsersQuery,
    useSetCanBecomeAdminMutation,
} from '@/store/api/services/generated/usersApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { type GlobalRoleAssignment, Prototype, Scope } from '@/types/roles';
import styles from './people-table.module.scss';
import { getPeopleTableColumns } from './people-table-columns';

function filterUsers(users: UsersGet[], searchTerm?: string) {
    if (!searchTerm) {
        return users;
    }
    return users.filter(
        (user) =>
            user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            user.last_name.toLowerCase().includes(searchTerm.toLowerCase()),
    );
}

export function PeoplePage() {
    const { t } = useTranslation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        {' '}
                        <TeamOutlined /> {t('People')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);

    const { data: { users = [] } = {}, isFetching } = useGetUsersQuery();
    const { data: { roles = [] } = {} } = useGetRolesQuery(Scope.GLOBAL);
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_USER });
    const canAssignGlobalRole = access?.allowed ?? false;

    const [searchTerm, setSearchTerm] = useState('');
    const filteredUsers = useMemo(() => filterUsers(users, searchTerm), [users, searchTerm]);
    const [createGlobalRoleAssignment] = useCreateGlobalRoleAssignmentMutation();
    const [updateGlobalRoleAssignment] = useModifyGlobalRoleAssignmentMutation();
    const [decideGlobalRoleAssignment] = useDecideGlobalRoleAssignmentMutation();
    const [deleteGlobalRoleAssignment] = useDeleteGlobalRoleAssignmentMutation();
    const [canBecomeAdmin] = useSetCanBecomeAdminMutation();

    const onChangeGlobalRole = useCallback(
        (user_id: string, value: string, original: GlobalRoleAssignment | null) => {
            if (original?.role.id === value) {
                return;
            }
            if (original !== null && !value) {
                deleteGlobalRoleAssignment(original.id)
                    .unwrap()
                    .then(() => {
                        dispatchMessage({
                            content: t('Global role assignment successfully reset'),
                            type: 'success',
                        });
                    })
                    .catch(() => {
                        dispatchMessage({ content: t('Could not reset global role assignment'), type: 'error' });
                    });
            }
            if (original !== null && value) {
                updateGlobalRoleAssignment({
                    id: original.id,
                    modifyGlobalRoleAssignment: {
                        role_id: value,
                    },
                })
                    .unwrap()
                    .then(() => {
                        dispatchMessage({
                            content: t('Global role assignment successfully changed'),
                            type: 'success',
                        });
                    })
                    .catch(() => {
                        dispatchMessage({ content: t('Could not change global role assignment'), type: 'error' });
                    });
            }
            if (original === null && value) {
                createGlobalRoleAssignment({
                    user_id,
                    role_id: value,
                })
                    .unwrap()
                    .then((result: GlobalRoleAssignmentResponse) => {
                        decideGlobalRoleAssignment({
                            id: result.id,
                            decideGlobalRoleAssignment: {
                                decision: 'approved',
                            },
                        })
                            .unwrap()
                            .then(() => {
                                dispatchMessage({
                                    content: t('Global role successfully assigned'),
                                    type: 'success',
                                });
                            })
                            .catch(() => {
                                dispatchMessage({ content: t('Could not assign global role'), type: 'error' });
                            });
                    })
                    .catch(() => {
                        dispatchMessage({ content: t('Could not assign global role'), type: 'error' });
                    });
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

    const columns = useMemo(
        () =>
            getPeopleTableColumns({
                t,
                users: filteredUsers,
                canAssignRole: canAssignGlobalRole,
                allRoles: roles.filter((role) => role.prototype !== Prototype.ADMIN),
                onChange: onChangeGlobalRole,
                changeCheckbox: async (user_id: string, can_become_admin: boolean) => {
                    await canBecomeAdmin({ user_id, can_become_admin });
                },
            }),
        [t, filteredUsers, roles, canAssignGlobalRole, onChangeGlobalRole, canBecomeAdmin],
    );

    return (
        <SearchPage
            title={t('People')}
            onChange={(e) => setSearchTerm(e.target.value)}
            searchPlaceholder={t('Search people by name')}
        >
            <Table<UsersGet>
                columns={columns}
                dataSource={filteredUsers}
                pagination={{
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} people', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                rowClassName={styles.row}
                size={'small'}
            />
        </SearchPage>
    );
}
