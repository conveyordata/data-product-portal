import styles from '@/pages/platforms-configs/components/platforms-configs-table/platforms-configs-table.module.scss';
import { Flex, Table, Typography, Checkbox, type CheckboxChangeEvent, Button, Space, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCallback, useState } from 'react';
import { InfoCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

export function RolesTable() {
    const { t } = useTranslation();

    const [data, setData] = useState([
        {
            key: '1',
            permission: 'View User Management Table',
            access: {
                'Super User': true,
                'Superintendent': true,
                'Device Manager': true,
                'Financial Executive': true,
            },
        },
        {
            key: '2',
            permission: 'Bulk Edit',
            access: {
                'Super User': true,
                'Superintendent': false,
                'Device Manager': false,
                'Financial Executive': false,
            },
        },
        {
            key: '3',
            permission: 'Log In As',
            access: {
                'Super User': true,
                'Superintendent': true,
                'Device Manager': false,
                'Financial Executive': false,
            },
        },
        {
            key: '4',
            permission: 'Role Management',
            access: {
                'Super User': true,
                'Superintendent': true,
                'Device Manager': true,
                'Financial Executive': false,
            },
        },
    ]);

    const handleCheckboxChange = useCallback(
        (record, key: string, value: boolean) => {
            const updatedData = data.map((item) => {
                if (item.key === record.key) {
                    return {
                        ...item,
                        access: {
                            ...item.access,
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

    const renderCheckbox = (key: string) => (value: boolean, record) => {
        return (
            <Flex justify={'center'}>
                <Checkbox
                    checked={value}
                    onChange={(e: CheckboxChangeEvent) => handleCheckboxChange(record, key, e.target.checked)}
                />
            </Flex>
        );
    };

    const createColumn = (title: string, description: string) => {
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
            key: title,
            render: renderCheckbox(title),
        };
    };

    const roleColumns = [
        { title: 'Super User', description: 'The super user' },
        { title: 'Superintendent', description: 'The superintendent' },
        { title: 'Device Manager', description: 'The device manager' },
        { title: 'Financial Executive', description: 'The financial executive' },
    ].map((item) => createColumn(item.title, item.description));

    const columns = [
        {
            title: 'Permission',
            dataIndex: 'permission',
            key: 'permission',
        },
        ...roleColumns,
    ];

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Roles')}</Typography.Title>
                <Button className={styles.formButton} type={'primary'}>
                    {t('Create new role')}
                </Button>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table columns={columns} dataSource={data} />
            </Flex>
        </Flex>
    );
}
