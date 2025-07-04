import { Flex, Form, Input, Pagination, Table, Typography } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

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
import { type GlobalRoleAssignmentContract, Scope } from '@/types/roles/role.contract';
import type { SearchForm } from '@/types/shared';
import type { UsersGetContract } from '@/types/users/user.contract';
import styles from './people-table.module.scss';
import { getPeopleTableColumns } from './people-table-columns';

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

export function PeopleTable() {
    const { t } = useTranslation();
    const { data: users = [], isFetching } = useGetAllUsersQuery();
    const { data: roles = [] } = useGetRolesQuery(Scope.GLOBAL);
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_USER });
    const canAssignGlobalRole = access?.allowed ?? false;

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredUsers = useMemo(() => filterUsers(users, searchTerm), [users, searchTerm]);
    const { pagination, handlePaginationChange } = useTablePagination(filteredUsers);
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
                allRoles: roles,
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
                        <Input.Search placeholder={t('Search people by name')} allowClear />
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
                            t('Showing {{range0}}-{{range1}} of {{count}} people', {
                                range0: range[0],
                                range1: range[1],
                                count: total,
                            })
                        }
                    />
                </Flex>

                <Table<UsersGetContract[0]>
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
