import styles from './roles-table.module.scss';
import { Flex, Table, Typography, Checkbox, type CheckboxChangeEvent, Button, Space, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCallback, useState } from 'react';
import { InfoCircleOutlined } from '@ant-design/icons';
import type { ColumnType } from 'antd/es/table/interface';

const { Text } = Typography;

type PermissionType = 'Group' | 'Instance';

type PermissionInstance = {
    type: PermissionType;
    permission: string;
    description: string;
    access: Map<string, string>;
};

type PermissionGroup = {
    type: PermissionType;
    name: string;
};

type Permission = PermissionInstance | PermissionGroup;

export function RolesTable() {
    const { t } = useTranslation();

    const [data, setData] = useState<Permission[]>([
        {
            type: 'Group',
            name: 'User Management',
        },
        {
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
            type: 'Group',
            name: 'Role Management',
        },
        {
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
                <Space className={styles.permissionInstance}>
                    <Text>{record.permission}</Text>
                    <Tooltip title={record.description}>
                        <InfoCircleOutlined />
                    </Tooltip>
                </Space>
            );
        } else if (record.type === 'Group') {
            record = record as PermissionGroup;
            return (
                <Space className={styles.permissionGroup}>
                    <Text strong>{record.name}</Text>
                </Space>
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
                <Space>
                    <Text>{title}</Text>
                    <Tooltip title={description}>
                        <InfoCircleOutlined />
                    </Tooltip>
                </Space>
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
        },
        ...roleColumns,
    ];

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Global roles')}</Typography.Title>
                <Button className={styles.formButton} type={'primary'}>
                    {t('Create new global role')}
                </Button>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table columns={columns} dataSource={data} pagination={false} rowKey={'permission'} />
            </Flex>
        </Flex>
    );
}
