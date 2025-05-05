import { AppstoreOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { useTranslation } from 'react-i18next';

import { DataProductOutlined, DatasetOutlined } from '@/components/icons';

export type CustomPendingRequestsTabKey = 'all' | 'dataProduct' | 'dataset';

interface SelectableTabsProps {
    activeKey: CustomPendingRequestsTabKey;
    onTabChange: (key: CustomPendingRequestsTabKey) => void;
}

export const SelectableTabs = ({ activeKey, onTabChange }: SelectableTabsProps) => {
    const { t } = useTranslation();

    const handleChange = (key: string) => {
        const typedKey = key as CustomPendingRequestsTabKey;
        onTabChange(typedKey);
    };

    const items = [
        {
            key: 'all',
            icon: <AppstoreOutlined />,
            title: t('All Requests'),
        },
        {
            key: 'dataset',
            icon: <DatasetOutlined />,
            title: t('Dataset'),
        },
        {
            key: 'dataProduct',
            icon: <DataProductOutlined />,
            title: t('Data Product'),
        },
    ];

    return (
        <Tabs
            activeKey={activeKey}
            onChange={handleChange}
            items={items.map(({ key, title, icon }) => ({
                key,
                label: title,
                icon,
                children: null,
            }))}
        />
    );
};
