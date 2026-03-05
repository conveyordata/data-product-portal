import { AppstoreOutlined } from '@ant-design/icons';
import { Tabs, type TabsProps } from 'antd';
import type { CSSProperties, ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';

export type CustomPendingRequestsTabKey = 'all' | 'dataProduct' | 'dataset';

interface SelectableTabsProps {
    activeKey: CustomPendingRequestsTabKey;
    onTabChange: (key: CustomPendingRequestsTabKey) => void;
    extra?: ReactNode;
    style?: CSSProperties;
}

export const SelectableTabs = ({ activeKey, onTabChange, extra, style }: SelectableTabsProps) => {
    const { t } = useTranslation();

    const handleChange = (key: string) => {
        const typedKey = key as CustomPendingRequestsTabKey;
        onTabChange(typedKey);
    };

    const items: TabsProps['items'] = [
        {
            key: 'all',
            icon: <AppstoreOutlined />,
            label: t('All Requests'),
        },
        {
            key: 'dataset',
            icon: <DatasetOutlined />,
            label: t('Output Port'),
        },
        {
            key: 'dataProduct',
            icon: <DataProductOutlined />,
            label: t('Data Product'),
        },
    ];

    return (
        <Tabs activeKey={activeKey} onChange={handleChange} items={items} tabBarExtraContent={extra} style={style} />
    );
};
