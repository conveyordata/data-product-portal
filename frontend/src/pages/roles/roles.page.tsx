import { GlobalOutlined } from '@ant-design/icons';
import type { TabsProps } from 'antd';
import { Flex, Tabs, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { CreateRoleButton } from '@/pages/roles/components/roles-button.component';
import { RolesTable } from '@/pages/roles/components/roles-table.component';
import { Scope } from '@/types/roles/role.contract';

const { Paragraph } = Typography;

type TabItem = Required<TabsProps>['items'][number];

export function RoleConfiguration() {
    const { t } = useTranslation();
    const [current, setCurrent] = useState<Scope>(Scope.GLOBAL);

    const items: TabItem[] = [
        {
            label: t('Global'),
            key: Scope.GLOBAL,
            icon: <GlobalOutlined />,
        },
        {
            label: t('Data Product'),
            key: Scope.DATA_PRODUCT,
            icon: <DataProductOutlined />,
        },
        {
            label: t('Dataset'),
            key: Scope.DATASET,
            icon: <DatasetOutlined />,
        },
    ];

    const onChange: TabsProps['onChange'] = (key) => {
        setCurrent(key as Scope);
    };

    return (
        <div>
            <Flex justify="space-between">
                <Typography.Title level={3}>{t('Manage Roles')}</Typography.Title>
                <CreateRoleButton scope={current} />
            </Flex>
            <Paragraph>{t('Roles are reusable sets of permissions.')}</Paragraph>

            <Tabs onChange={onChange} activeKey={current} items={items} />
            <RolesTable scope={current} />
        </div>
    );
}
