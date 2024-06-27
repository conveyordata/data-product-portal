import { Tabs } from 'antd';
import { ReactNode, useMemo } from 'react';
import styles from './dataset-tabs.module.scss';
import Icon, { HistoryOutlined, InfoCircleOutlined, PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { ExplorerTab } from './explorer-tab/explorer-tab';
import { HistoryTab } from './history-tab/history-tab';
import { DataProductTab } from '@/pages/dataset/components/dataset-tabs/data-product-tab/data-product-tab.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import { AboutTab } from './about-tab/about-tab.tsx';
import { TeamTab } from './team-tab/team-tab.tsx';
import { ReactFlowProvider } from 'reactflow';

type Props = {
    datasetId: string;
    isLoading: boolean;
};

enum TabKeys {
    About = 'about',
    DataProduct = 'data-product',
    Team = 'team',
    Explorer = 'explorer',
    History = 'history',
}

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DatasetTabs({ datasetId, isLoading }: Props) {
    const { t } = useTranslation();

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('About'),
                key: TabKeys.About,
                icon: <InfoCircleOutlined />,
                children: <AboutTab datasetId={datasetId} />,
            },
            {
                label: t('Data Products'),
                key: TabKeys.DataProduct,
                icon: <Icon component={dataProductOutlineIcon} />,
                children: <DataProductTab datasetId={datasetId} />,
            },
            {
                label: t('Team'),
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab datasetId={datasetId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <PartitionOutlined />,
                children: (
                    <ReactFlowProvider>
                        <ExplorerTab datasetId={datasetId} />
                    </ReactFlowProvider>
                ),
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

    return (
        <Tabs
            defaultActiveKey={TabKeys.About}
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
