import { RolesTable } from '@/pages/roles/components/roles-table.component.tsx';
import { Flex, Tabs, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { TabsProps } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { RolesButton } from '@/pages/roles/components/roles-button.component.tsx';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';

const { Paragraph } = Typography;

type TabItem = Required<TabsProps>['items'][number];

export type RoleScope = 'global' | 'data_products' | 'datasets';

export function RoleConfiguration() {
    const { t } = useTranslation();
    const [current, setCurrent] = useState<RoleScope>('global');

    const items: TabItem[] = [
        {
            label: t('Global'),
            key: 'global',
            icon: <GlobalOutlined />,
        },
        {
            label: t('Data Products'),
            key: 'data_products',
            icon: <DataProductOutlined />,
        },
        {
            label: t('Datasets'),
            key: 'datasets',
            icon: <DatasetOutlined />,
        },
    ];

    const onChange: TabsProps['onChange'] = (key) => {
        setCurrent(key as RoleScope);
    };

    return (
        <div>
            <Flex justify="space-between">
                <Typography.Title level={2}>{t('Manage Roles')}</Typography.Title>
                <RolesButton scope={current} />
            </Flex>
            <Paragraph>{t('Roles are reusable sets of permissions.')}</Paragraph>

            <Tabs onChange={onChange} activeKey={current} items={items} />
            <RolesTable scope={current} />
        </div>
    );
}
