import { Checkbox, type CheckboxChangeEvent, Flex, Table, Typography } from 'antd';
import type { ColumnType } from 'antd/es/table/interface';
import { useCallback, useEffect, useMemo, useState } from 'react';

import QuestionTooltip from '@/components/tooltip/question-tooltip.tsx';
import type { RoleScope } from '@/pages/roles/roles.page.tsx';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice.ts';

import styles from './roles-table.module.scss';

const { Text } = Typography;

type Role = {
    name: string;
    description: string;
};

type PermissionType = 'Group' | 'Instance';

type PermissionBase = {
    type: PermissionType;
    id: number | string;
    name: string;
};

type PermissionInstance = PermissionBase & {
    type: 'Instance';
    description: string;
    access: Map<string, string>;
};

type PermissionGroup = PermissionBase & {
    type: 'Group';
};

type Permission = PermissionInstance | PermissionGroup;

type RolesTableProps = {
    scope: RoleScope;
};
export function RolesTable({ scope }: RolesTableProps) {
    const { data: roles = [], isFetching } = useGetRolesQuery(scope);

    const joinedRoles: Role[] = useMemo(() => [...loadRolesForScope(scope), ...roles], [roles, scope]);
    const [data, setData] = useState<Permission[]>(loadStateForScope(scope));

    useEffect(() => {
        setData(loadStateForScope(scope));
    }, [scope]);

    const handleCheckboxChange = useCallback(
        (record: PermissionInstance, key: string, value: boolean) => {
            const updatedData = data.map((item) => {
                if (item.type === 'Instance' && item.id === record.id) {
                    return {
                        ...item,
                        access: {
                            ...(item as PermissionInstance).access,
                            [key]: value,
                        },
                    };
                }
                return item;
            });

            setData(updatedData);
        },
        [data],
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

    const renderCheckbox = (key: string) => (value: boolean, record: Permission) => {
        if (record.type === 'Instance') {
            return (
                <Flex justify={'center'}>
                    <Checkbox
                        checked={value}
                        onChange={(e: CheckboxChangeEvent) =>
                            handleCheckboxChange(record as PermissionInstance, key, e.target.checked)
                        }
                    />
                </Flex>
            );
        }
    };

    const createColumn = (title: string, description: string): ColumnType<Permission> => {
        return {
            title: (
                <QuestionTooltip title={description}>
                    <Text>{title}</Text>
                </QuestionTooltip>
            ),
            dataIndex: ['access', title],
            render: renderCheckbox(title),
        };
    };

    const roleColumns = joinedRoles.map((item) => createColumn(item.name, item.description));

    const columns: ColumnType<Permission>[] = [
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
                loading={isFetching}
                dataSource={data}
                pagination={false}
                rowKey={'id'}
                scroll={{ x: 'max-content' }}
            />
        </Flex>
    );
}

function loadRolesForScope(scope: RoleScope): Role[] {
    switch (scope) {
        case 'global':
            return [
                {
                    name: 'Admin',
                    description: 'Administrators have blanket permissions',
                },
                {
                    name: 'Everyone',
                    description: "This is the role that is used as fallback for users that don't have another role",
                },
            ];
        case 'data_product':
            return [
                {
                    name: 'Owner',
                    description: 'The owner of a Data Product',
                },
                {
                    name: 'Solution Architect',
                    description: 'The Solution Architect for a Data Product',
                },
                {
                    name: 'Member',
                    description: 'A regular team member of a Data Product',
                },
            ];
        case 'dataset':
            return [
                {
                    name: 'Owner',
                    description: 'The owner of a Dataset',
                },
                {
                    name: 'Solution Architect',
                    description: 'The Solution Architect for a Dataset',
                },
                {
                    name: 'Member',
                    description: 'A regular team member of a Dataset',
                },
            ];
    }
}

function loadStateForScope(scope: RoleScope): Permission[] {
    switch (scope) {
        case 'global':
            return [
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
                    access: {
                        Admin: true,
                        Everyone: false,
                    },
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
                    access: {
                        Admin: true,
                        Everyone: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 103,
                    name: 'Create Dataset',
                    description: 'Allows the creation of a Dataset',
                    access: {
                        Admin: true,
                        Everyone: false,
                    },
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
                    access: {
                        Admin: true,
                        Everyone: true,
                    },
                },
                {
                    type: 'Instance',
                    id: 105,
                    name: 'Request Dataset access',
                    description: 'Allows requesting access to a Dataset',
                    access: {
                        Admin: true,
                        Everyone: true,
                    },
                },
            ];
        case 'data_product':
            return [
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 302,
                    name: 'Manage settings',
                    description: 'Allows changing the settings of a Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 303,
                    name: 'Manage status',
                    description: 'Allows changing the status of a Data Product',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 304,
                    name: 'Delete Data Product',
                    description: 'Allows the role to delete the Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 307,
                    name: 'Remove User',
                    description: 'Allows removing a user as member from this Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 306,
                    name: 'Modify User',
                    description: 'Allows changing the role of a member of the Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 308,
                    name: 'Review access request',
                    description: 'Allows accepting or rejecting an access request made for the Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 311,
                    name: 'Remove and unlink Data Output',
                    description: 'Allows removing a Data Output from this Data Product and unlinking it from a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 310,
                    name: 'Modify Data Output',
                    description: 'Allows modifying the details of a Data Output of this Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 312,
                    name: 'Request Data Output Link',
                    description: 'Allows to request that a Data Output of Data Product gets linked to a Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: true,
                    },
                },
                {
                    type: 'Instance',
                    id: 314,
                    name: 'Remove Access to Dataset',
                    description: 'Allows to remove read access to a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: true,
                    },
                },
            ];
        case 'dataset':
            return [
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 402,
                    name: 'Manage settings',
                    description: 'Allows changing the settings of a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 403,
                    name: 'Manage status',
                    description: 'Allows changing the status of a Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 404,
                    name: 'Delete Dataset',
                    description: 'Allows the role to delete the Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 407,
                    name: 'Remove User',
                    description: 'Allows removing a user as member from this Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 406,
                    name: 'Modify User',
                    description: 'Allows changing the role of a member of the Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 408,
                    name: 'Review access request',
                    description: 'Allows approving or rejecting an access request made for the Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
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
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 410,
                    name: 'Remove Data Output link',
                    description: 'Allows unlinking Data Outputs from the Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    type: 'Instance',
                    id: 412,
                    name: 'Revoke Data Product Access',
                    description: 'Allows the role to revoke read access from a data product again',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
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
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: true,
                    },
                },
            ];
    }
}
