import { Tabs } from 'antd';
import { ReactNode, useMemo } from 'react';
// import { ExplorerTab } from '@/pages/data-output/components/data-output-tabs/explorer-tab/explorer-tab.tsx';
// import { TeamTab } from '@/pages/data-output/components/data-output-tabs/team-tab/team-tab.tsx';
// import { HistoryTab } from '@/pages/data-output/components/data-output-tabs/history-tab/history-tab.tsx';
import styles from './data-output-tabs.module.scss';
import Icon, { HistoryOutlined, InfoCircleOutlined, PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
// import { DataOutputTab } from '@/pages/data-output/components/data-output-tabs/data-output-tab/data-output-tab.tsx';
import { DatasetTab } from '@/pages/data-output/components/data-output-tabs/dataset-tab/dataset-tab.tsx';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
// import { AboutTab } from '@/pages/data-output/components/data-output-tabs/about-tab/about-tab.tsx';
import { ReactFlowProvider } from 'reactflow';

type Props = {
    dataOutputId: string;
    isLoading: boolean;
};

enum TabKeys {
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

export function DataOutputTabs({ dataOutputId, isLoading }: Props) {
    const { t } = useTranslation();

    const tabs: Tab[] = useMemo(() => {
        return [
            // {
            //     label: t('About'),
            //     key: TabKeys.About,
            //     icon: <InfoCircleOutlined />,
            //     children: <AboutTab dataOutputId={dataOutputId} />,
            // },
            {
                label: t('Datasets'),
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataOutputId={dataOutputId} />,
            },
            // {
            //     label: t('Team'),
            //     key: TabKeys.Team,
            //     icon: <TeamOutlined />,
            //     children: <TeamTab dataOutputId={dataOutputId} />,
            // },
            // {
            //     label: t('Explorer'),
            //     key: TabKeys.Explorer,
            //     icon: <PartitionOutlined />,
            //     children: (
            //         <ReactFlowProvider>
            //             <ExplorerTab dataOutputId={dataOutputId} />
            //         </ReactFlowProvider>
            //     ),
            // },
            // {
            //     label: t('History'),
            //     key: TabKeys.History,
            //     icon: <HistoryOutlined />,
            //     children: <HistoryTab dataOutputId={dataOutputId} />,
            // },
        ];
    }, [dataOutputId, t]);

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
                    disabled: !dataOutputId,
                    className: styles.tabPane,
                };
            })}
            size={'middle'}
            rootClassName={styles.tabContainer}
        />
    );
}
