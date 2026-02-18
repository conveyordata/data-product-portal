import { InboxOutlined } from '@ant-design/icons';
import { Badge, Tabs, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { useGetPendingActionsQuery } from '@/store/features/pending-actions/pending-actions-api-slice';
import { DataProductsTab } from './components/data-products-tab/data-products-tab.component';
import { OutputPortsTab } from './components/output-ports-tab/output-ports-tab.component';
import { RequestsPanel } from './components/requests-panel/requests-panel.component';
import { TabKeys } from './product-studio-tabkeys';

export function ProductStudio() {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<string>(TabKeys.DataProducts);
    const { data: pendingActions } = useGetPendingActionsQuery();

    useEffect(() => {
        const hash = location.hash.slice(1);
        if (hash && Object.values(TabKeys).includes(hash as TabKeys)) {
            setActiveTab(hash);
        } else if (!hash) {
            // If no hash is present, set the default tab hash
            navigate(`#${TabKeys.DataProducts}`, { replace: true });
        }
    }, [location.hash, navigate]);

    const onTabChange = (key: string) => {
        setActiveTab(key);
        navigate(`#${key}`, { replace: true });
    };

    const pendingCount = pendingActions?.length ?? 0;

    const tabs = [
        {
            key: TabKeys.DataProducts,
            label: t('Data Products'),
            icon: <DataProductOutlined />,
            children: <DataProductsTab />,
        },
        {
            key: TabKeys.OutputPorts,
            label: t('Output Ports'),
            icon: <DatasetOutlined />,
            children: <OutputPortsTab />,
        },
        {
            key: TabKeys.Requests,
            label: (
                <Badge count={pendingCount} offset={[10, 0]}>
                    {t('Requests')}
                </Badge>
            ),
            icon: <InboxOutlined />,
            children: <RequestsPanel />,
        },
    ];

    return (
        <div>
            <Typography.Title level={3}>{t('Product Studio')}</Typography.Title>
            <Typography.Paragraph>
                {t(
                    'Manage your Data Products and Output Ports. View, edit, and monitor all your data assets in one place.',
                )}
            </Typography.Paragraph>
            <Tabs activeKey={activeTab} items={tabs} onChange={onTabChange} />
        </div>
    );
}
