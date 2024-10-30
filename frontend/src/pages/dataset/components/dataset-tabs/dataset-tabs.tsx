import { Tabs } from 'antd';
import { ReactNode, useEffect, useMemo, useState } from 'react';
import styles from './dataset-tabs.module.scss';
import Icon, { HistoryOutlined, InfoCircleOutlined, PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { ExplorerTab } from './explorer-tab/explorer-tab';
import { HistoryTab } from './history-tab/history-tab';
import { DataProductTab } from '@/pages/dataset/components/dataset-tabs/data-product-tab/data-product-tab.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import { DataOutputTab } from '@/pages/dataset/components/dataset-tabs/data-output-tab/data-output-tab.tsx';
import { AboutTab } from './about-tab/about-tab.tsx';
import { TeamTab } from './team-tab/team-tab.tsx';
import { ReactFlowProvider } from 'reactflow';
import { useLocation, useNavigate } from 'react-router-dom';

type Props = {
    datasetId: string;
    isLoading: boolean;
};

export enum TabKeys {
    About = 'about',
    DataProduct = 'data-product',
    DataOutput = 'data-output',
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
                label: t('Data Outputs'),
                key: TabKeys.DataOutput,
                icon: <Icon component={dataOutputOutlineIcon} />,
                children: <DataOutputTab datasetId={datasetId} />,
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

    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.About);

    useEffect(() => {
        const hash = location.hash.slice(1);
        if(hash) {
            setActiveTab(hash);
        }
    }, [location])

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
