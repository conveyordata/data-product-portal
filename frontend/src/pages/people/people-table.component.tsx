import { Table } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import SearchPage from '@/components/search-page/search-page.component.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useCreateGlobalRoleAssignmentMutation,
    useDecideGlobalRoleAssignmentMutation,
    useDeleteGlobalRoleAssignmentMutation,
    useUpdateGlobalRoleAssignmentMutation,
} from '@/store/features/role-assignments/global-roles-api-slice.ts';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice.ts';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { type GlobalRoleAssignmentContract, Prototype, Scope } from '@/types/roles/role.contract.ts';
import type { UsersGetContract } from '@/types/users/user.contract.ts';
import styles from './people-table.module.scss';
import { getPeopleTableColumns } from './people-table-columns.tsx';

function filterUsers(users: UsersGetContract, searchTerm?: string) {
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
    const { data: users = [], isFetching } = useGetAllUsersQuery();
    const { data: roles = [] } = useGetRolesQuery(Scope.GLOBAL);
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_USER });
    const canAssignGlobalRole = access?.allowed ?? false;
    const [searchTerm, setSearchTerm] = useState('');

    const filteredUsers = useMemo(() => filterUsers(users, searchTerm), [users, searchTerm]);
    const [createGlobalRoleAssignment] = useCreateGlobalRoleAssignmentMutation();
    const [updateGlobalRoleAssignment] = useUpdateGlobalRoleAssignmentMutation();
    const [decideGlobalRoleAssignment] = useDecideGlobalRoleAssignmentMutation();
    const [deleteGlobalRoleAssignment] = useDeleteGlobalRoleAssignmentMutation();

    const onChangeGlobalRole = useCallback(
        (user_id: string, value: string, original: GlobalRoleAssignmentContract | null) => {
            if (original?.role.id === value) {
                return;
            }
            if (original !== null && !value) {
                deleteGlobalRoleAssignment({
                    role_assignment_id: original.id,
                })
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
                    role_assignment_id: original.id,
                    role_id: value,
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
                    .then((result: GlobalRoleAssignmentContract) => {
                        decideGlobalRoleAssignment({
                            role_assignment_id: result.id,
                            decision_status: 'approved',
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
            }),
        [t, filteredUsers, roles, canAssignGlobalRole, onChangeGlobalRole],
    );

    return (
        <SearchPage title={t('People')} onSearch={setSearchTerm} searchPlaceholder={t('Search people by name')}>
            <Table<UsersGetContract[0]>
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
