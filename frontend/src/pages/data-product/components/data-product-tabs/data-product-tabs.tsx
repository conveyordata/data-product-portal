import Icon, {
    BarChartOutlined,
    CompassOutlined,
    HistoryOutlined,
    InfoCircleOutlined,
    SettingOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { Badge, Flex, Tabs } from 'antd';
import { type ReactElement, type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';

import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { Explorer } from '@/components/explorer/explorer';
import { HistoryTab } from '@/components/history/history-tab';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { AboutTab } from '@/pages/data-product/components/data-product-tabs/about-tab/about-tab.tsx';
import { DataOutputTab } from '@/pages/data-product/components/data-product-tabs/data-output-tab/data-output-tab.tsx';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { DatasetTab } from '@/pages/data-product/components/data-product-tabs/dataset-tab/dataset-tab.tsx';
import { TeamTab } from '@/pages/data-product/components/data-product-tabs/team-tab/team-tab.tsx';
import { useGetDataProductHistoryQuery } from '@/store/features/data-products/data-products-api-slice';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { UsageTab } from '../../../../components/tabs/usage-tab/usage-tab';
import styles from './data-product-tabs.module.scss';
import { SettingsTab } from './settings-tab/settings-tab';

type Props = {
    dataProductId: string;
    isLoading: boolean;
};

type Tab = {
    label: string | ReactElement;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DataProductTabs({ dataProductId, isLoading }: Props) {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const { data: dataProductHistoryData, isLoading: isFetchingDataProductHistory } = useGetDataProductHistoryQuery(
        dataProductId,
        { skip: !dataProductId },
    );
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.About);

    useEffect(() => {
        posthog.capture(PosthogEvents.DATA_PRODUCTS_TAB_CLICKED, {
            tab_name: activeTab,
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
                children: <AboutTab dataProductId={dataProductId} />,
            },
            {
                label: (
                    <Flex className={styles.betaContainer}>
                        {t('Usage')}
                        <Badge className={styles.beta} count={t('BETA')} />
                    </Flex>
                ),
                key: TabKeys.Usage,
                icon: <BarChartOutlined />,
                children: <UsageTab dataProductId={dataProductId} />,
            },
            {
                label: t('Input Datasets'),
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataProductId={dataProductId} />,
            },
            {
                label: t('Data Outputs'),
                key: TabKeys.DataOutputs,
                icon: <Icon component={dataOutputOutlineIcon} />,
                children: <DataOutputTab dataProductId={dataProductId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <CompassOutlined />,
                children: <Explorer id={dataProductId} type={'dataproduct'} />,
            },
            {
                label: t('Team'),
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab dataProductId={dataProductId} />,
            },
            {
                label: t('Settings'),
                key: TabKeys.Settings,
                icon: <SettingOutlined />,
                children: <SettingsTab dataProductId={dataProductId} />,
            },
            {
                label: t('History'),
                key: TabKeys.History,
                icon: <HistoryOutlined />,
                children: (
                    <HistoryTab
                        id={dataProductId}
                        type={EventReferenceEntity.DataProduct}
                        history={dataProductHistoryData}
                        isFetching={isFetchingDataProductHistory}
                    />
                ),
            },
        ];
    }, [dataProductId, t, dataProductHistoryData, isFetchingDataProductHistory]);

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
                    disabled: !dataProductId,
                    className: styles.tabPane,
                };
            })}
            size={'middle'}
            rootClassName={styles.tabContainer}
            onChange={onTabChange}
        />
    );
}
