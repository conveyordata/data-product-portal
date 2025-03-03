import { GlobalOutlined } from '@ant-design/icons';
import type { TabsProps } from 'antd';
import { Flex, Tabs, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { RolesButton } from '@/pages/roles/components/roles-button.component.tsx';
import { RolesTable } from '@/pages/roles/components/roles-table.component.tsx';

const { Paragraph } = Typography;

type TabItem = Required<TabsProps>['items'][number];

export type RoleScope = 'global' | 'data_product' | 'dataset';

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
            label: t('Data Product'),
            key: 'data_product',
            icon: <DataProductOutlined />,
        },
        {
            label: t('Dataset'),
            key: 'dataset',
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
