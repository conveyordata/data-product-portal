import { AppstoreOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { NotificationTypes } from '@/types/notifications/notification.contract';

export type CustomTabKey = 'all' | 'dataProduct' | 'dataset';

interface SelectableTabsProps {
    onSelectChange?: (types: Set<NotificationTypes>) => void;
}

export const SelectableTabs = ({ onSelectChange }: SelectableTabsProps) => {
    const { t } = useTranslation();

    const [activeKey, setActiveKey] = useState<CustomTabKey>('all');

    const handleChange = (key: string) => {
        const typedKey = key as CustomTabKey;
        setActiveKey(typedKey);

        const typesSet = new Set<NotificationTypes>();

        if (typedKey === 'all') {
            Object.values(NotificationTypes).forEach((type) => typesSet.add(type));
        } else {
            if (typedKey === 'dataProduct') {
                typesSet.add(NotificationTypes.DataProductMembershipNotification);
            } else if (typedKey === 'dataset') {
                typesSet.add(NotificationTypes.DataOutputDatasetNotification);
                typesSet.add(NotificationTypes.DataProductDatasetNotification);
            }
        }

        onSelectChange?.(typesSet);
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
            style={{ width: '100%' }}
            items={items.map(({ key, title, icon }) => ({
                key,
                label: title,
                icon,
                children: null,
            }))}
        />
    );
};
