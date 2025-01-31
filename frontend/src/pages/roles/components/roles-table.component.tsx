import styles from './roles-table.module.scss';
import { Flex, Table, Typography, Checkbox, type CheckboxChangeEvent } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCallback, useState } from 'react';
import type { ColumnType } from 'antd/es/table/interface';
import type { RoleScope } from '@/pages/roles/roles.page.tsx';
import QuestionTooltip from '@/components/tooltip/question-tooltip.tsx';

const { Text } = Typography;

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
    const { t } = useTranslation();

    const [data, setData] = useState<Permission[]>([
        {
            order: 1,
            type: 'Group',
            name: 'User Management',
        },
        {
            order: 2,
            type: 'Instance',
            permission: 'View User Management Table',
            description: 'Interesting info on user management',
            access: {
                'Super User': true,
                Superintendent: true,
                'Device Manager': true,
                'Financial Executive': true,
            },
        },
        {
            order: 3,
            type: 'Instance',
            permission: 'Bulk Edit',
            description: 'Interesting info on bulking',
            access: {
                'Super User': true,
                Superintendent: false,
                'Device Manager': false,
                'Financial Executive': false,
            },
        },
        {
            order: 4,
            type: 'Instance',
            permission: 'Log In As',
            description: 'Interesting info on logging in',
            access: {
                'Super User': true,
                Superintendent: true,
                'Device Manager': false,
                'Financial Executive': false,
            },
        },
        {
            order: 5,
            type: 'Group',
            name: 'Role Management',
        },
        {
            order: 6,
            type: 'Instance',
            permission: 'Role Management',
            description: 'Interesting info on managing roles',
            access: {
                'Super User': true,
                Superintendent: true,
                'Device Manager': true,
                'Financial Executive': false,
            },
        },
    ]);

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

    const roleColumns = [
        { title: 'Super User', description: 'The super user' },
        { title: 'Superintendent', description: 'The superintendent' },
        { title: 'Device Manager', description: 'The device manager' },
        { title: 'Financial Executive', description: 'The financial executive' },
    ].map((item) => createColumn(item.title, item.description));

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
            <Flex vertical className={styles.tableFilters}>
                <Table
                    columns={columns}
                    dataSource={data}
                    pagination={false}
                    rowKey={'order'}
                    scroll={{ x: 'max-content' }}
                />
            </Flex>
        </Flex>
    );
}
