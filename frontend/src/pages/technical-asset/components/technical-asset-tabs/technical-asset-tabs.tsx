import { CodeOutlined, CompassOutlined, HistoryOutlined, SettingOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';

import { EnvironmentSettingsSection } from '@/components/environment-settings/environment-settings-section.component.tsx';
import { Explorer } from '@/components/explorer/explorer.tsx';
import { HistoryTab } from '@/components/history/history-tab';
import { OutputPortOutlined } from '@/components/icons';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { OutputPortTab } from '@/pages/technical-asset/components/technical-asset-tabs/output-port-tab/output-port-tab.tsx';
import { TabKeys } from '@/pages/technical-asset/components/technical-asset-tabs/technical-asset-tabkeys.ts';
import {
    type GetTechnicalAssetResponse,
    useGetTechnicalAssetEventHistoryQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import styles from './technical-asset-tabs.module.scss';
import { TechnologiesTab } from './technologies-tab/technologies-tab';

type Props = {
    technicalAsset: GetTechnicalAssetResponse;
    dataProductId: string;
    canEdit: boolean;
    isLoading: boolean;
};

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function TechnicalAssetTabs({ technicalAsset, dataProductId, canEdit, isLoading }: Props) {
    const { t } = useTranslation();
    const technicalAssetId = technicalAsset.id;

    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.OutputPorts);
    const historyQuery = useGetTechnicalAssetEventHistoryQuery(
        { id: technicalAssetId, dataProductId },
        { skip: !technicalAssetId },
    );
    const { data: { events: dataOutputHistoryData = [] } = {} } = historyQuery;

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
                key: TabKeys.OutputPorts,
                icon: <OutputPortOutlined />,
                children: <OutputPortTab dataProductId={dataProductId} technicalAssetId={technicalAssetId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <CompassOutlined />,
                children: <Explorer id={technicalAssetId} type="dataoutput" dataProductId={dataProductId} />,
            },
            {
                label: t('Technical information'),
                key: TabKeys.Technologies,
                icon: <CodeOutlined />,
                children: <TechnologiesTab technicalAssetId={technicalAssetId} dataProductId={dataProductId} />,
            },
            {
                label: t('Settings'),
                key: TabKeys.Settings,
                icon: <SettingOutlined />,
                children: (
                    <EnvironmentSettingsSection
                        dataProductId={dataProductId}
                        technicalAsset={technicalAsset}
                        canEdit={canEdit}
                    />
                ),
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
                        query={historyQuery}
                    />
                ),
            },
        ];
    }, [technicalAssetId, technicalAsset, canEdit, t, dataOutputHistoryData, historyQuery, dataProductId]);

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
            size="middle"
            rootClassName={styles.tabContainer}
            onChange={onTabChange}
        />
    );
}
