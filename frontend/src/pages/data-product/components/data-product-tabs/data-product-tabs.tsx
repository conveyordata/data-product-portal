import { Tabs } from 'antd';
import { ReactNode, useEffect, useMemo, useState } from 'react';
import { ExplorerTab } from '@/pages/data-product/components/data-product-tabs/explorer-tab/explorer-tab.tsx';
import { TeamTab } from '@/pages/data-product/components/data-product-tabs/team-tab/team-tab.tsx';
import { HistoryTab } from '@/pages/data-product/components/data-product-tabs/history-tab/history-tab.tsx';
import styles from './data-product-tabs.module.scss';
import Icon, { HistoryOutlined, InfoCircleOutlined, PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataOutputTab } from '@/pages/data-product/components/data-product-tabs/data-output-tab/data-output-tab.tsx';
import { DatasetTab } from '@/pages/data-product/components/data-product-tabs/dataset-tab/dataset-tab.tsx';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import { AboutTab } from '@/pages/data-product/components/data-product-tabs/about-tab/about-tab.tsx';
import { ReactFlowProvider } from 'reactflow';
import { useLocation, useNavigate } from 'react-router-dom';

type Props = {
    dataProductId: string;
    isLoading: boolean;
};

export enum TabKeys {
    About = 'about',
    DataOutputs = 'dataoutputs',
    Datasets = 'datasets',
    Explorer = 'explorer',
    Team = 'team',
    History = 'history',
}

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DataProductTabs({ dataProductId, isLoading }: Props) {
    const { t } = useTranslation();

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('About'),
                key: TabKeys.About,
                icon: <InfoCircleOutlined />,
                children: <AboutTab dataProductId={dataProductId} />,
            },
            {
                label: t('Datasets'),
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataProductId={dataProductId} />,
            },
            {
                label: t('Team'),
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab dataProductId={dataProductId} />,
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
                icon: <PartitionOutlined />,
                children: (
                    <ReactFlowProvider>
                        <ExplorerTab dataProductId={dataProductId} />
                    </ReactFlowProvider>
                ),
            },
            {
                label: t('History'),
                key: TabKeys.History,
                icon: <HistoryOutlined />,
                children: <HistoryTab dataProductId={dataProductId} />,
            },
        ];
    }, [dataProductId, t]);

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
