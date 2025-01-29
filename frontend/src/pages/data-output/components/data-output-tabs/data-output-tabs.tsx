import { Tabs } from 'antd';
import { ReactNode, useEffect, useMemo, useState } from 'react';
import styles from './data-output-tabs.module.scss';
import Icon, { CodeOutlined, PartitionOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DatasetTab } from '@/pages/data-output/components/data-output-tabs/dataset-tab/dataset-tab.tsx';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { TechnologiesTab } from './technologies-tab/technologies-tab';
import { ReactFlowProvider } from 'reactflow';
import { Explorer } from '@/components/explorer/explorer';
import { useLocation, useNavigate } from 'react-router-dom';

type Props = {
    dataOutputId: string;
    isLoading: boolean;
};

export enum TabKeys {
    Datasets = 'datasets',
    Technologies = 'technologies',
    Explorer = 'explorer',
}

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DataOutputTabs({ dataOutputId, isLoading }: Props) {
    const { t } = useTranslation();

    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.Datasets);

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
                label: t('Datasets'),
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataOutputId={dataOutputId} />,
            },
            {
                label: t('Technical information'),
                key: TabKeys.Technologies,
                icon: <CodeOutlined />,
                children: <TechnologiesTab dataOutputId={dataOutputId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <PartitionOutlined />,
                children: (
                    <ReactFlowProvider>
                        <Explorer id={dataOutputId} type={'dataoutput'} />
                    </ReactFlowProvider>
                ),
            },
        ];
    }, [dataOutputId, t]);

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
                    disabled: !dataOutputId,
                    className: styles.tabPane,
                };
            })}
            size={'middle'}
            rootClassName={styles.tabContainer}
            onChange={onTabChange}
        />
    );
}
