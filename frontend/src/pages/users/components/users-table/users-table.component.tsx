import { Flex, Form, Input, Pagination, Table, Typography } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useCreateGlobalRoleAssignmentMutation,
    useDecideGlobalRoleAssignmentMutation,
    useDeleteGlobalRoleAssignmentMutation,
    useUpdateGlobalRoleAssignmentMutation,
} from '@/store/features/role-assignments/global-roles-api-slice';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { createUserIdPath } from '@/types/navigation';
import type { GlobalRoleAssignmentContract } from '@/types/roles/role.contract';
import type { SearchForm } from '@/types/shared';
import type { UsersGetContract } from '@/types/users/user.contract';
import styles from './users-table.module.scss';
import { getUserTableColumns } from './users-table-columns';

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

export function UsersTable() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { data: users = [], isFetching } = useGetAllUsersQuery();
    const { data: roles = [] } = useGetRolesQuery('global');
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_USER });
    const canAssignGlobalRole = access?.allowed ?? false;

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredUsers = useMemo(() => filterUsers(users, searchTerm), [users, searchTerm]);
    const { pagination, handlePaginationChange } = useTablePagination(filteredUsers);
    const [createGlobalRole] = useCreateGlobalRoleAssignmentMutation();
    const [updateGlobalRole] = useUpdateGlobalRoleAssignmentMutation();
    const [decideGlobalRole] = useDecideGlobalRoleAssignmentMutation();
    const [deleteGlobalRole] = useDeleteGlobalRoleAssignmentMutation();

    function navigateToUser(userId: string) {
        navigate(createUserIdPath(userId));
    }

    const onChangeGlobalRole = useCallback(
        (user_id: string, value: string, original: GlobalRoleAssignmentContract | null) => {
            if (original?.role.id === value) {
                return;
            }
            if (original !== null && !value) {
                deleteGlobalRole({
                    role_assignment_id: original.id,
                })
                    .unwrap()
                    .then(() => {
                        dispatchMessage({
                            content: t('Global role removed successfully'),
                            type: 'success',
                        });
                    })
                    .catch(() => {
                        dispatchMessage({ content: t('Could not remove global role'), type: 'error' });
                    });
            }
            if (original !== null && value) {
                updateGlobalRole({
                    role_assignment_id: original.id,
                    role_id: value,
                })
                    .unwrap()
                    .then(() => {
                        dispatchMessage({
                            content: t('Global role updated successfully'),
                            type: 'success',
                        });
                    })
                    .catch(() => {
                        dispatchMessage({ content: t('Could not update global role'), type: 'error' });
                    });
            }
            if (original === null && value) {
                createGlobalRole({
                    user_id,
                    role_id: value,
                })
                    .unwrap()
                    .then((result: GlobalRoleAssignmentContract) => {
                        decideGlobalRole({
                            role_assignment_id: result.id,
                            decision_status: 'approved',
                        })
                            .unwrap()
                            .then(() => {
                                dispatchMessage({
                                    content: t('Global role created successfully'),
                                    type: 'success',
                                });
                            })
                            .catch(() => {
                                dispatchMessage({ content: t('Could not create global role'), type: 'error' });
                            });
                    })
                    .catch(() => {
                        dispatchMessage({ content: t('Could not create global role'), type: 'error' });
                    });
            }
        },
        [t, deleteGlobalRole, updateGlobalRole, createGlobalRole, decideGlobalRole],
    );

    const columns = useMemo(
        () =>
            getUserTableColumns({
                t,
                users: filteredUsers,
                canAssignRole: canAssignGlobalRole,
                allRoles: roles.filter((role) => role.name.toLowerCase() !== 'everyone'),
                onChange: onChangeGlobalRole,
            }),
        [t, filteredUsers, roles, canAssignGlobalRole, onChangeGlobalRole],
    );

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            ...pagination,
            current: page,
            pageSize,
        });
    };

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('People')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search users by name')} allowClear />
                    </Form.Item>
                </Form>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Flex align="flex-end" justify="flex-end" className={styles.tableBar}>
                    <Pagination
                        current={pagination.current}
                        pageSize={pagination.pageSize}
                        total={users.length}
                        onChange={handlePageChange}
                        size="small"
                        showTotal={(total, range) =>
                            t('Showing {{range0}}-{{range1}} of {{total}} users', {
                                range0: range[0],
                                range1: range[1],
                                total: total,
                            })
                        }
                    />
                </Flex>

                <Table<UsersGetContract[0]>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToUser(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredUsers}
                    pagination={{
                        ...pagination,
                        position: [],
                    }}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={styles.row}
                    size={'small'}
                />
            </Flex>
        </Flex>
    );
}
