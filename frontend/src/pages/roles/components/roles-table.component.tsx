import styles from './roles-table.module.scss';
import { Flex, Table, Typography, Checkbox, type CheckboxChangeEvent } from 'antd';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ColumnType } from 'antd/es/table/interface';
import type { RoleScope } from '@/pages/roles/roles.page.tsx';
import QuestionTooltip from '@/components/tooltip/question-tooltip.tsx';

const { Text } = Typography;

type Role = {
    title: string;
    description: string;
};

type PermissionType = 'Group' | 'Instance';

type PermissionInstance = {
    type: PermissionType;
    order: number;
    permission: string;
    description: string;
    access: Map<string, string>;
};

type PermissionGroup = {
    type: PermissionType;
    order: number;
    name: string;
};

type Permission = PermissionInstance | PermissionGroup;

type RolesTableProps = {
    scope: RoleScope;
};
export function RolesTable({ scope }: RolesTableProps) {
    const roles: Role[] = useMemo(() => loadRolesForScope(scope), [scope]);
    const [data, setData] = useState<Permission[]>(loadStateForScope(scope));

    useEffect(() => {
        setData(loadStateForScope(scope));
    }, [scope]);

    const handleCheckboxChange = useCallback(
        (record: PermissionInstance, key: string, value: boolean) => {
            const updatedData = data.map((item) => {
                if (item.type === 'Instance' && (item as PermissionInstance).permission === record.permission) {
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
                    <Text className={styles.permissionInstance}>{record.permission}</Text>
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

    const roleColumns = roles.map((item) => createColumn(item.title, item.description));

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
                dataSource={data}
                pagination={false}
                rowKey={'order'}
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
                    title: 'Admin',
                    description: 'Administrators have blanket permissions',
                },
                {
                    title: 'Everyone',
                    description: "This is the role that is used as fallback for users that don't have another role",
                },
            ];
        case 'data_product':
            return [
                {
                    title: 'Owner',
                    description: 'The owner of a Data Product',
                },
                {
                    title: 'Solution Architect',
                    description: 'The Solution Architect for a Data Product',
                },
                {
                    title: 'Member',
                    description: 'A regular team member of a Data Product',
                },
            ];
        case 'dataset':
            return [
                {
                    title: 'Owner',
                    description: 'The owner of a Dataset',
                },
                {
                    title: 'Solution Architect',
                    description: 'The Solution Architect for a Dataset',
                },
                {
                    title: 'Member',
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
                    order: 10,
                    type: 'Group',
                    name: 'Manage Installation',
                },
                {
                    order: 11,
                    type: 'Instance',
                    permission: 'Manage configuration',
                    description: 'Allows modifying the configuration options of this installation',
                    access: {
                        Admin: true,
                        Everyone: false,
                    },
                },
                {
                    order: 20,
                    type: 'Group',
                    name: 'Manage Assets',
                },
                {
                    order: 21,
                    type: 'Instance',
                    permission: 'Create Data Product',
                    description: 'Allows the creation of a Data Product',
                    access: {
                        Admin: true,
                        Everyone: false,
                    },
                },
                {
                    order: 22,
                    type: 'Instance',
                    permission: 'Create Dataset',
                    description: 'Allows the creation of a Dataset',
                    access: {
                        Admin: true,
                        Everyone: false,
                    },
                },
                {
                    order: 30,
                    type: 'Group',
                    name: 'Manage Access',
                },
                {
                    order: 31,
                    type: 'Instance',
                    permission: 'Request Data Product access',
                    description: 'Allows requesting access to a Data Product',
                    access: {
                        Admin: true,
                        Everyone: true,
                    },
                },
                {
                    order: 32,
                    type: 'Instance',
                    permission: 'Request Dataset access',
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
                    order: 10,
                    type: 'Group',
                    name: 'Manage Data Product',
                },
                {
                    order: 11,
                    type: 'Instance',
                    permission: 'Manage general properties',
                    description: 'Allows modifying properties such as labels and the description of a Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 12,
                    type: 'Instance',
                    permission: 'Manage settings',
                    description: 'Allows changing the settings of a Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 13,
                    type: 'Instance',
                    permission: 'Manage status',
                    description: 'Allows changing the status of a Data Product',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 14,
                    type: 'Instance',
                    permission: 'Delete Data Product',
                    description: 'Allows the role to delete the Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 20,
                    type: 'Group',
                    name: 'Manage Users',
                },
                {
                    order: 21,
                    type: 'Instance',
                    permission: 'Add User',
                    description: 'Allows adding a user as member to this Data Product and assigning a role',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 22,
                    type: 'Instance',
                    permission: 'Remove User',
                    description: 'Allows removing a user as member from this Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 23,
                    type: 'Instance',
                    permission: 'Modify User',
                    description: 'Allows changing the role of a member of the Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 24,
                    type: 'Instance',
                    permission: 'Review access request',
                    description: 'Allows approving or rejecting an access request made for the Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 30,
                    type: 'Group',
                    name: 'Manage Data Outputs',
                },
                {
                    order: 31,
                    type: 'Instance',
                    permission: 'Add Data Output',
                    description: 'Allows adding a Data Output to this Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 32,
                    type: 'Instance',
                    permission: 'Remove and unlink Data Output',
                    description: 'Allows removing a Data Output from this Data Product and unlinking it from a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 33,
                    type: 'Instance',
                    permission: 'Modify Data Output',
                    description: 'Allows modifying the details of a Data Output of this Data Product',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 34,
                    type: 'Instance',
                    permission: 'Request Data Output Link',
                    description: 'Allows to request that a Data Output of Data Product gets linked to a Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 40,
                    type: 'Group',
                    name: 'Manage Input Datasets',
                },
                {
                    order: 41,
                    type: 'Instance',
                    permission: 'Request Access to Dataset',
                    description: 'Allows to request read access to a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: true,
                    },
                },
                {
                    order: 42,
                    type: 'Instance',
                    permission: 'Remove Access to Dataset',
                    description: 'Allows to remove read access to a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 50,
                    type: 'Group',
                    name: 'Integrations',
                },
                {
                    order: 51,
                    type: 'Instance',
                    permission: 'Access Integrations',
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
                    order: 10,
                    type: 'Group',
                    name: 'Manage Dataset',
                },
                {
                    order: 11,
                    type: 'Instance',
                    permission: 'Manage general properties',
                    description: 'Allows modifying properties such as labels and the description of a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 12,
                    type: 'Instance',
                    permission: 'Manage settings',
                    description: 'Allows changing the settings of a Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 13,
                    type: 'Instance',
                    permission: 'Manage status',
                    description: 'Allows changing the status of a Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 14,
                    type: 'Instance',
                    permission: 'Delete Dataset',
                    description: 'Allows the role to delete the Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 20,
                    type: 'Group',
                    name: 'Manage Users',
                },
                {
                    order: 21,
                    type: 'Instance',
                    permission: 'Add User',
                    description: 'Allows adding a user as member to this Dataset and assigning a role',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 22,
                    type: 'Instance',
                    permission: 'Remove User',
                    description: 'Allows removing a user as member from this Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 23,
                    type: 'Instance',
                    permission: 'Modify User',
                    description: 'Allows changing the role of a member of the Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 24,
                    type: 'Instance',
                    permission: 'Review access request',
                    description: 'Allows approving or rejecting an access request made for the Dataset',
                    access: {
                        Owner: true,
                        'Solution Architect': false,
                        Member: false,
                    },
                },
                {
                    order: 30,
                    type: 'Group',
                    name: 'Manage Data Outputs',
                },
                {
                    order: 31,
                    type: 'Instance',
                    permission: 'Accept Data Output link',
                    description: 'Allows accepting a request to link a Data Output to the Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 32,
                    type: 'Instance',
                    permission: 'Remove Data Output link',
                    description: 'Allows unlinking Data Outputs from the Dataset',
                    access: {
                        Owner: false,
                        'Solution Architect': true,
                        Member: false,
                    },
                },
                {
                    order: 50,
                    type: 'Group',
                    name: 'Integrations',
                },
                {
                    order: 51,
                    type: 'Instance',
                    permission: 'Access Integrations',
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
