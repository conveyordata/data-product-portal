import { AppstoreOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { PendingActionTypes } from '@/types/pending-actions/pending-actions';

export type CustomTabKey = 'all' | 'dataProduct' | 'dataset';

interface SelectableTabsProps {
    onSelectChange?: (types: Set<PendingActionTypes>) => void;
}

export const SelectableTabs = ({ onSelectChange }: SelectableTabsProps) => {
    const { t } = useTranslation();

    const [activeKey, setActiveKey] = useState<CustomTabKey>('all');

    const handleChange = (key: string) => {
        const typedKey = key as CustomTabKey;
        setActiveKey(typedKey);

        const typesSet = new Set<PendingActionTypes>();

        if (typedKey === 'all') {
            Object.values(PendingActionTypes).forEach((type) => typesSet.add(type));
        } else {
            if (typedKey === 'dataProduct') {
                typesSet.add(PendingActionTypes.DataProductMembership);
            } else if (typedKey === 'dataset') {
                typesSet.add(PendingActionTypes.DataProductDataset);
                typesSet.add(PendingActionTypes.DataOutputDataset);
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
            items={items.map(({ key, title, icon }) => ({
                key,
                label: title,
                icon,
                children: null,
            }))}
        />
    );
};
