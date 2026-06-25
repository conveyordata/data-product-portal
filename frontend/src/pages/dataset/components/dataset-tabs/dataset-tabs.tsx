import {
    BarChartOutlined,
    CompassOutlined,
    FileTextOutlined,
    HistoryOutlined,
    InfoCircleOutlined,
    SettingOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Tabs } from 'antd';
import { type ReactNode, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Explorer } from '@/components/explorer/explorer.tsx';
import { HistoryTab } from '@/components/history/history-tab.tsx';
import { ConsumersIcon, TechnicalAssetOutlined } from '@/components/icons';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useTabParam } from '@/hooks/use-tab-param.tsx';
import { ConsumersTab } from '@/pages/dataset/components/dataset-tabs/consumers-tab/consumers-tab';
import { DataModelTab } from '@/pages/dataset/components/dataset-tabs/data-model-tab/data-model-tab';
import { DataOutputTab } from '@/pages/dataset/components/dataset-tabs/data-output-tab/data-output-tab';
import { TabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { UsageTab } from '@/pages/dataset/components/dataset-tabs/usage-tab/usage-tab.tsx';
import { useGetOutputPortsEventHistoryQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { EventReferenceEntity } from '@/types/events/event-reference-entity.ts';
import { AboutTab } from './about-tab/about-tab.tsx';
import styles from './dataset-tabs.module.scss';
import { SettingsTab } from './settings-tab/settings-tab';
import { TeamTab } from './team-tab/team-tab.tsx';

type Tab = {
    label: ReactNode;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

type Props = {
    datasetId: string;
    dataProductId: string;
    isLoading: boolean;
};

export function DatasetTabs({ datasetId, dataProductId, isLoading }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const { data: { events: datasetHistoryData = [] } = {}, isLoading: isFetchingDatasetHistory } =
        useGetOutputPortsEventHistoryQuery({ id: datasetId, dataProductId }, { skip: !datasetId });
    const { activeTab, onTabChange } = useTabParam(TabKeys.About, Object.values(TabKeys), (tab) =>
        posthog.capture(PosthogEvents.OUTPUT_PORT_TAB, { tab }),
    );

    useEffect(() => {
        posthog.capture(PosthogEvents.MARKETPLACE_DATASET_TAB_CLICKED, {
            tab_name: activeTab,
        });
    }, [activeTab, posthog]);

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('About'),
                key: TabKeys.About,
                icon: <InfoCircleOutlined />,
                children: <AboutTab datasetId={datasetId} dataProductId={dataProductId} />,
            },
            {
                label: t('Data Model'),
                key: TabKeys.DataModel,
                icon: <FileTextOutlined />,
                children: <DataModelTab datasetId={datasetId} dataProductId={dataProductId} />,
            },
            {
                label: t('Usage'),
                key: TabKeys.Usage,
                icon: <BarChartOutlined />,
                children: <UsageTab outputPortId={datasetId} dataProductId={dataProductId} />,
            },
            {
                label: t('Technical Assets'),
                key: TabKeys.Producers,
                icon: <TechnicalAssetOutlined />,
                children: <DataOutputTab datasetId={datasetId} dataProductId={dataProductId} />,
            },

            {
                label: t('Consumers'),
                key: TabKeys.Consumers,
                icon: <ConsumersIcon />,
                children: <ConsumersTab outputPortId={datasetId} dataProductId={dataProductId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <CompassOutlined />,
                children: <Explorer id={datasetId} type={'dataset'} dataProductId={dataProductId} />,
            },
            {
                label: t('Team'),
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab datasetId={datasetId} dataProductId={dataProductId} />,
            },
            {
                label: t('Settings'),
                key: TabKeys.Settings,
                icon: <SettingOutlined />,
                children: <SettingsTab datasetId={datasetId} dataProductId={dataProductId} />,
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
    }, [datasetId, t, datasetHistoryData, isFetchingDatasetHistory, dataProductId]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <Tabs
            activeKey={activeTab}
            onChange={onTabChange}
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
        />
    );
}
