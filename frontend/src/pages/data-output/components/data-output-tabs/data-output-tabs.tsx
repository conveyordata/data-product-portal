import Icon, { CodeOutlined, PartitionOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router';
import { ReactFlowProvider } from 'reactflow';

import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { Explorer } from '@/components/explorer/explorer';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys.ts';
import { DatasetTab } from '@/pages/data-output/components/data-output-tabs/dataset-tab/dataset-tab.tsx';

import styles from './data-output-tabs.module.scss';
import { TechnologiesTab } from './technologies-tab/technologies-tab';

type Props = {
    dataOutputId: string;
    isLoading: boolean;
};

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
