import Icon, { CodeOutlined, CompassOutlined, HistoryOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';

import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { Explorer } from '@/components/explorer/explorer';
import { HistoryTab } from '@/components/history/history-tab';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys.ts';
import { DatasetTab } from '@/pages/data-output/components/data-output-tabs/dataset-tab/dataset-tab.tsx';
import { useGetTechnicalAssetEventHistoryQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import styles from './data-output-tabs.module.scss';
import { TechnologiesTab } from './technologies-tab/technologies-tab';

type Props = {
    technicalAssetId: string;
    dataProductId: string;
    isLoading: boolean;
};

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DataOutputTabs({ technicalAssetId, dataProductId, isLoading }: Props) {
    const { t } = useTranslation();

    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.Datasets);
    const { data: { events: dataOutputHistoryData = [] } = {}, isLoading: isFetchingDataOutputHistory } =
        useGetTechnicalAssetEventHistoryQuery({ id: technicalAssetId, dataProductId }, { skip: !technicalAssetId });

    useEffect(() => {
        const hash = location.hash.slice(1);
        if (hash) {
            setActiveTab(hash);
        }
    }, [location]);

    const onTabChange = (key: string) => {
        navigate(`#${key}`);
    };

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('Output Ports'),
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataProductId={dataProductId} technicalAssetId={technicalAssetId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <CompassOutlined />,
                children: <Explorer id={technicalAssetId} type={'dataoutput'} dataProductId={dataProductId} />,
            },
            {
                label: t('Technical information'),
                key: TabKeys.Technologies,
                icon: <CodeOutlined />,
                children: <TechnologiesTab technicalAssetId={technicalAssetId} dataProductId={dataProductId} />,
            },
            {
                label: t('History'),
                key: TabKeys.History,
                icon: <HistoryOutlined />,
                children: (
                    <HistoryTab
                        id={technicalAssetId}
                        type={EventReferenceEntity.DataOutput}
                        history={dataOutputHistoryData}
                        isFetching={isFetchingDataOutputHistory}
                    />
                ),
            },
        ];
    }, [technicalAssetId, t, dataOutputHistoryData, isFetchingDataOutputHistory, dataProductId]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <Tabs
            activeKey={activeTab}
            items={tabs.map(({ key, label, icon, children }) => {
                return {
                    label,
                    key,
                    children,
                    icon,
                    disabled: !technicalAssetId,
                    className: styles.tabPane,
                };
            })}
            size={'middle'}
            rootClassName={styles.tabContainer}
            onChange={onTabChange}
        />
    );
}
