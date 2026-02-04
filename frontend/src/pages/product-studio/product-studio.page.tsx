import { Tabs, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { DataProductsTab } from './components/data-products-tab/data-products-tab.component';
import { OutputPortsTab } from './components/output-ports-tab/output-ports-tab.component';
import { TabKeys } from './product-studio-tabkeys';

export function ProductStudio() {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<string>(TabKeys.DataProducts);

    useEffect(() => {
        const hash = location.hash.slice(1);
        if (hash && Object.values(TabKeys).includes(hash as TabKeys)) {
            setActiveTab(hash);
        }
    }, [location.hash]);

    const onTabChange = (key: string) => {
        setActiveTab(key);
        navigate(`#${key}`, { replace: true });
    };

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
    ];

    return (
        <div>
            <Typography.Title level={3}>{t('Product Studio')}</Typography.Title>
            <Typography.Paragraph>
                {t(
                    'Manage your data products and output ports. View, edit, and monitor all your data assets in one place.',
                )}
            </Typography.Paragraph>
            <Tabs activeKey={activeTab} items={tabs} onChange={onTabChange} />
        </div>
    );
}
