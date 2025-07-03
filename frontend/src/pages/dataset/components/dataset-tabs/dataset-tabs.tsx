import { CompassOutlined, HistoryOutlined, InfoCircleOutlined, SettingOutlined, TeamOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';

import { Explorer } from '@/components/explorer/explorer';
import { HistoryTab } from '@/components/history/history-tab.tsx';
import { DataOutputOutlined, DataProductOutlined } from '@/components/icons';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { DataOutputTab } from '@/pages/dataset/components/dataset-tabs/data-output-tab/data-output-tab';
import { DataProductTab } from '@/pages/dataset/components/dataset-tabs/data-product-tab/data-product-tab';
import { TabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetDatasetHistoryQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { EventReferenceEntity } from '@/types/events/event-reference-entity.ts';

import { AboutTab } from './about-tab/about-tab.tsx';
import styles from './dataset-tabs.module.scss';
import { SettingsTab } from './settings-tab/settings-tab';
import { TeamTab } from './team-tab/team-tab.tsx';
import posthog from '@/config/posthog-config.ts';

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

type Props = {
    datasetId: string;
    isLoading: boolean;
};

export function DatasetTabs({ datasetId, isLoading }: Props) {
    const { t } = useTranslation();

    const location = useLocation();
    const navigate = useNavigate();

    const { data: datasetHistoryData, isLoading: isFetchingDatasetHistory } = useGetDatasetHistoryQuery(datasetId, {
        skip: !datasetId,
    });
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.About);

    useEffect(() => {
        posthog.capture('marketplace_dataset_tab_viewed', {
            tab_name: activeTab
        });
    }, [activeTab]);

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
                label: t('Consuming Data Products'),
                key: TabKeys.DataProduct,
                icon: <DataProductOutlined />,
                children: <DataProductTab datasetId={datasetId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <CompassOutlined />,
                children: <Explorer id={datasetId} type={'dataset'} />,
            },
            {
                label: t('Team'),
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab datasetId={datasetId} />,
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
                children: (
                    <HistoryTab
                        id={datasetId}
                        type={EventReferenceEntity.Dataset}
                        history={datasetHistoryData}
                        isFetching={isFetchingDatasetHistory}
                    />
                ),
            },
        ];
    }, [datasetId, t, datasetHistoryData, isFetchingDatasetHistory]);

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
