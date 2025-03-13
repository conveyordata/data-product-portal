import {
    HistoryOutlined,
    InfoCircleOutlined,
    PartitionOutlined,
    SettingOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { Tabs } from 'antd';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';

import { Explorer } from '@/components/explorer/explorer';
import { DataOutputOutlined, DataProductOutlined } from '@/components/icons';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { DataOutputTab } from '@/pages/dataset/components/dataset-tabs/data-output-tab/data-output-tab';
import { DataProductTab } from '@/pages/dataset/components/dataset-tabs/data-product-tab/data-product-tab';
import { TabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';

import { AboutTab } from './about-tab/about-tab.tsx';
import styles from './dataset-tabs.module.scss';
import { HistoryTab } from './history-tab/history-tab';
import { SettingsTab } from './settings-tab/settings-tab';
import { TeamTab } from './team-tab/team-tab.tsx';

type Props = {
    datasetId: string;
    isLoading: boolean;
};

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DatasetTabs({ datasetId, isLoading }: Props) {
    const { t } = useTranslation();

    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.About);

    useEffect(() => {
        const hash = location.hash.slice(1);
        if (hash) {
            setActiveTab(hash);
        }
    }, [location]);

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('About'),
                key: TabKeys.About,
                icon: <InfoCircleOutlined />,
                children: <AboutTab datasetId={datasetId} />,
            },
            {
                label: t('Producing Data Products'),
                key: TabKeys.DataOutput,
                icon: <DataOutputOutlined />,
                children: <DataOutputTab datasetId={datasetId} />,
            },
            {
                label: t('Dataset Owners'),
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab datasetId={datasetId} />,
            },
            {
                label: t('Consuming Data Products'),
                key: TabKeys.DataProduct,
                icon: <DataProductOutlined />,
                children: <DataProductTab datasetId={datasetId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <PartitionOutlined />,
                children: <Explorer id={datasetId} type={'dataset'} />,
            },
            {
                label: t('Settings'),
                key: TabKeys.Settings,
                icon: <SettingOutlined />,
                children: <SettingsTab datasetId={datasetId} />,
            },
            {
                label: t('History'),
                key: TabKeys.History,
                icon: <HistoryOutlined />,
                children: <HistoryTab datasetId={datasetId} />,
            },
        ];
    }, [datasetId, t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    const onTabChange = (key: string) => {
        navigate(`#${key}`);
    };

    return (
        <Tabs
            activeKey={activeTab}
            items={tabs.map(({ key, label, icon, children }) => {
                return {
                    label,
                    key,
                    children,
                    icon,
                    disabled: !datasetId,
                    className: styles.tabPane,
                };
            })}
            size={'middle'}
            rootClassName={styles.tabContainer}
            onChange={onTabChange}
        />
    );
}
