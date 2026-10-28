import { InboxOutlined, ProductOutlined } from '@ant-design/icons';
import { Badge, Space, Tabs, Typography, theme } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductOutlined, ExplorationOutlined, OutputPortOutlined } from '@/components/icons';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useTabParam } from '@/hooks/use-tab-param.tsx';
import { ExplorationsTab } from '@/pages/product-studio/components/explorations-tab/explorations-tab.component';
import { MyRequestsTab } from '@/pages/product-studio/components/my-requests-tab/my-requests-panel.tsx';
import { PendingAccessRequestsTab } from '@/pages/product-studio/components/pending-access-requests-tab/pending-access-requests-tab.tsx';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi';
import { DataProductsTab } from './components/data-products-tab/data-products-tab.component';
import { OutputPortsTab } from './components/output-ports-tab/output-ports-tab.component';
import { TabKeys } from './product-studio-tabkeys';

export function ProductStudio() {
    const { t } = useTranslation();
    const { token } = theme.useToken();

    const { activeTab, onTabChange } = useTabParam(TabKeys.DataProducts, Object.values(TabKeys));

    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined /> {t('Product Studio')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);

    const { data: { pending_actions } = {} } = useGetUserPendingActionsQuery();

    const pendingCount = pending_actions?.length ?? 0;

    const tabs = [
        {
            key: TabKeys.DataProducts,
            label: t('Data Products'),
            icon: <DataProductOutlined />,
            children: <DataProductsTab />,
        },
        {
            key: TabKeys.Explorations,
            label: t('Explorations'),
            icon: <ExplorationOutlined />,
            children: <ExplorationsTab />,
        },
        {
            key: TabKeys.OutputPorts,
            label: t('Output Ports'),
            icon: <OutputPortOutlined />,
            children: <OutputPortsTab />,
        },
        {
            key: TabKeys.MyRequests,
            label: t('My Requests'),
            icon: <InboxOutlined />,
            children: <MyRequestsTab />,
        },
        {
            key: TabKeys.PendingRequests,
            label: (
                <Space>
                    {t('Pending Requests')}
                    <Badge count={pendingCount} color={token.colorPrimary} />
                </Space>
            ),
            icon: <InboxOutlined />,
            children: <PendingAccessRequestsTab />,
        },
    ];

    return (
        <div>
            <Typography.Title level={3}>{t('Product Studio')}</Typography.Title>
            <Typography.Paragraph>
                {t(
                    'Manage your Data Products, Explorations and Output Ports. View, edit, and monitor all your data assets in one place.',
                )}
            </Typography.Paragraph>
            <Tabs activeKey={activeTab} items={tabs} onChange={onTabChange} />
        </div>
    );
}
