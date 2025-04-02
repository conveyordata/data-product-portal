import { Checkbox, type CheckboxChangeEvent, Flex, Table, type TableColumnType,Typography } from 'antd';
import { type ReactElement, useCallback, useMemo } from 'react';

import QuestionTooltip from '@/components/tooltip/question-tooltip';
import type { RoleScope } from '@/pages/roles/roles.page';
import { useGetRolesQuery, useUpdateRoleMutation } from '@/store/features/roles/roles-api-slice';
import type { RoleContract } from '@/types/roles';
import { Prototype } from '@/types/roles/role.contract';

import styles from './roles-table.module.scss';

const { Text } = Typography;

type PermissionType = 'Group' | 'Instance';

type PermissionBase = {
    type: PermissionType;
    id: number | string;
    name: string;
};

type PermissionInstance = PermissionBase & {
    type: 'Instance';
    id: number;
    description: string;
    access?: object;
};

type PermissionGroup = PermissionBase & {
    type: 'Group';
    id: string;
};

type Permission = PermissionInstance | PermissionGroup;

function prototypePrecedence(role_a: RoleContract, role_b: RoleContract) {
    const a = role_a.prototype;
    const b = role_b.prototype;

    if (a === b) {
        return 0;
    }
    if (a === Prototype.ADMIN) {
        return -1;
    }
    if (b === Prototype.ADMIN) {
        return 1;
    }
    if (a === Prototype.EVERYONE) {
        return -1;
    }
    if (b === Prototype.EVERYONE) {
        return 1;
    }
    if (a === Prototype.OWNER) {
        return -1;
    }
    if (b === Prototype.OWNER) {
        return 1;
    }
    return 0;
}

type RolesTableProps = {
    scope: RoleScope;
};
export function RolesTable({ scope }: RolesTableProps) {
    const { data: rawRoles = [], isFetching } = useGetRolesQuery(scope);
    const [updateRole, { isLoading }] = useUpdateRoleMutation();

    const roles = useMemo(() => {
        const data = [...rawRoles];
        data.sort(prototypePrecedence);
        return [...data];
    }, [rawRoles]);
    const permissions = useMemo(() => determinePermissionsForScope(scope, roles), [roles, scope]);

    const handleCheckboxChange = useCallback(
        (record: PermissionInstance, id: string, checked: boolean) => {
            console.log(record, id, checked);
            const role = roles.find((role) => role.id === id)!;

            const permissions = [...role.permissions];
            if (checked && !permissions.includes(record.id)) {
                permissions.push(record.id);
            } else if (!checked && permissions.includes(record.id)) {
                const index = permissions.indexOf(record.id);
                permissions.splice(index, 1);
            }

            updateRole({ id: role.id, permissions });
        },
        [roles, updateRole],
    );

    const renderPermission = (_: string, record: Permission) => {
        if (record.type === 'Instance') {
            record = record as PermissionInstance;
            return (
                <QuestionTooltip title={record.description}>
                    <Text className={styles.permissionInstance}>{record.name}</Text>
                </QuestionTooltip>
            );
        } else if (record.type === 'Group') {
            record = record as PermissionGroup;
            return (
                <Text className={styles.permissionGroup} strong>
                    {record.name}
                </Text>
            );
        }
    };

    const renderCheckbox = (id: string) => (value: boolean, record: Permission) => {
        if (record.type === 'Instance') {
            const role = roles.find((role) => role.id === id)!;

            let checkbox: ReactElement;
            if (role.prototype === Prototype.ADMIN) {
                checkbox = <Checkbox checked={true} disabled />;
            } else {
                checkbox = (
                    <Checkbox
                        checked={value}
                        onChange={(e: CheckboxChangeEvent) =>
                            handleCheckboxChange(record as PermissionInstance, id, e.target.checked)
                        }
                    />
                );
            }

            return <Flex justify={'center'}>{checkbox}</Flex>;
        }
    };

    const createColumn = (title: string, id: string, description: string): TableColumnType<Permission> => {
        return {
            title: (
                <QuestionTooltip title={description}>
                    <Text>{title}</Text>
                </QuestionTooltip>
            ),
            dataIndex: ['access', id],
            render: renderCheckbox(id),
        };
    };

    const roleColumns = roles.map((role) => createColumn(role.name, role.id, role.description));

    const columns: TableColumnType<Permission>[] = [
        {
            dataIndex: 'permission',
            fixed: 'left',
            className: styles.permissionsColumn,
            render: renderPermission,
            ellipsis: false,
            onCell: () => ({
                style: { whiteSpace: 'nowrap' },
            }),
        },
        ...roleColumns,
    ];

    return (
        <Flex vertical className={styles.tableContainer}>
            <Table
                columns={columns}
                loading={isFetching || isLoading}
                dataSource={permissions}
                pagination={false}
                rowKey={'id'}
                scroll={{ x: 'max-content' }}
            />
        </Flex>
    );
}

function determinePermissionsForScope(scope: RoleScope, roles: RoleContract[]): Permission[] {
    let permissions: Permission[] = [];

    switch (scope) {
        case 'global':
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Installation',
                    name: 'Manage Installation',
                },
                {
                    type: 'Instance',
                    id: 101,
                    name: 'Manage configuration',
                    description: 'Allows modifying the configuration options of this installation',
                },
                {
                    type: 'Group',
                    id: 'Manage Assets',
                    name: 'Manage Assets',
                },
                {
                    type: 'Instance',
                    id: 102,
                    name: 'Create Data Product',
                    description: 'Allows the creation of a Data Product',
                },
                {
                    type: 'Instance',
                    id: 103,
                    name: 'Create Dataset',
                    description: 'Allows the creation of a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Access',
                    name: 'Manage Access',
                },
                {
                    type: 'Instance',
                    id: 104,
                    name: 'Request Data Product access',
                    description: 'Allows requesting access to a Data Product',
                },
                {
                    type: 'Instance',
                    id: 105,
                    name: 'Request Dataset access',
                    description: 'Allows requesting access to a Dataset',
                },
            ];
            break;
        case 'data_product':
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Data Product',
                    name: 'Manage Data Product',
                },
                {
                    type: 'Instance',
                    id: 301,
                    name: 'Manage general properties',
                    description: 'Allows modifying properties such as labels and the description of a Data Product',
                },
                {
                    type: 'Instance',
                    id: 302,
                    name: 'Manage settings',
                    description: 'Allows changing the settings of a Data Product',
                },
                {
                    type: 'Instance',
                    id: 303,
                    name: 'Manage status',
                    description: 'Allows changing the status of a Data Product',
                },
                {
                    type: 'Instance',
                    id: 304,
                    name: 'Delete Data Product',
                    description: 'Allows the role to delete the Data Product',
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: 'Manage Users',
                },
                {
                    type: 'Instance',
                    id: 305,
                    name: 'Add User',
                    description: 'Allows adding a user as member to this Data Product and assigning a role',
                },
                {
                    type: 'Instance',
                    id: 307,
                    name: 'Remove User',
                    description: 'Allows removing a user as member from this Data Product',
                },
                {
                    type: 'Instance',
                    id: 306,
                    name: 'Modify User',
                    description: 'Allows changing the role of a member of the Data Product',
                },
                {
                    type: 'Instance',
                    id: 308,
                    name: 'Review access request',
                    description: 'Allows accepting or rejecting an access request made for the Data Product',
                },
                {
                    type: 'Group',
                    id: 'Manage Data Outputs',
                    name: 'Manage Data Outputs',
                },
                {
                    type: 'Instance',
                    id: 309,
                    name: 'Add Data Output',
                    description: 'Allows adding a Data Output to this Data Product',
                },
                {
                    type: 'Instance',
                    id: 311,
                    name: 'Remove and unlink Data Output',
                    description: 'Allows removing a Data Output from this Data Product and unlinking it from a Dataset',
                },
                {
                    type: 'Instance',
                    id: 310,
                    name: 'Modify Data Output',
                    description: 'Allows modifying the details of a Data Output of this Data Product',
                },
                {
                    type: 'Instance',
                    id: 312,
                    name: 'Request Data Output Link',
                    description: 'Allows to request that a Data Output of Data Product gets linked to a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Input Datasets',
                    name: 'Manage Input Datasets',
                },
                {
                    type: 'Instance',
                    id: 313,
                    name: 'Request Access to Dataset',
                    description: 'Allows to request read access to a Dataset',
                },
                {
                    type: 'Instance',
                    id: 314,
                    name: 'Remove Access to Dataset',
                    description: 'Allows to remove read access to a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Integrations',
                    name: 'Integrations',
                },
                {
                    type: 'Instance',
                    id: 315,
                    name: 'Access Integrations',
                    description: 'Allows the role to see and access Integrations of the Data Product',
                },
            ];
            break;
        case 'dataset':
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Dataset',
                    name: 'Manage Dataset',
                },
                {
                    type: 'Instance',
                    id: 401,
                    name: 'Manage general properties',
                    description: 'Allows modifying properties such as labels and the description of a Dataset',
                },
                {
                    type: 'Instance',
                    id: 402,
                    name: 'Manage settings',
                    description: 'Allows changing the settings of a Dataset',
                },
                {
                    type: 'Instance',
                    id: 403,
                    name: 'Manage status',
                    description: 'Allows changing the status of a Dataset',
                },
                {
                    type: 'Instance',
                    id: 404,
                    name: 'Delete Dataset',
                    description: 'Allows the role to delete the Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: 'Manage Users',
                },
                {
                    type: 'Instance',
                    id: 405,
                    name: 'Add User',
                    description: 'Allows adding a user as member to this Dataset and assigning a role',
                },
                {
                    type: 'Instance',
                    id: 407,
                    name: 'Remove User',
                    description: 'Allows removing a user as member from this Dataset',
                },
                {
                    type: 'Instance',
                    id: 406,
                    name: 'Modify User',
                    description: 'Allows changing the role of a member of the Dataset',
                },
                {
                    type: 'Instance',
                    id: 408,
                    name: 'Review access request',
                    description: 'Allows approving or rejecting an access request made for the Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Data Outputs',
                    name: 'Manage Data Outputs',
                },
                {
                    type: 'Instance',
                    id: 409,
                    name: 'Accept Data Output link',
                    description: 'Allows accepting a request to link a Data Output to the Dataset',
                },
                {
                    type: 'Instance',
                    id: 410,
                    name: 'Remove Data Output link',
                    description: 'Allows unlinking Data Outputs from the Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Read Access',
                    name: 'Manage Read Access',
                },
                {
                    type: 'Instance',
                    id: 411,
                    name: 'Approve Data Product Access',
                    description: 'Allows the role to accept or reject a read access request from a data product',
                },
                {
                    type: 'Instance',
                    id: 412,
                    name: 'Revoke Data Product Access',
                    description: 'Allows the role to revoke read access from a data product again',
                },
                {
                    type: 'Group',
                    id: 'Integrations',
                    name: 'Integrations',
                },
                {
                    type: 'Instance',
                    id: 413,
                    name: 'Access Integrations',
                    description: 'Allows the role to see and access Integrations of the Dataset',
                },
            ];
            break;
    }

    const determineAccess = (permission: number) => {
        return Object.fromEntries(roles.map((role) => [role.id, role.permissions.includes(permission)]));
    };

    for (const permission of permissions) {
        if (permission.type === 'Instance') {
            permission.access = determineAccess(permission.id);
        }
    }

    return permissions;
}
