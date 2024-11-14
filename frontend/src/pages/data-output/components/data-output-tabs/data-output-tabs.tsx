import { Tabs } from 'antd';
import { ReactNode, useMemo } from 'react';
import styles from './data-output-tabs.module.scss';
import Icon, { FileProtectOutlined, CodeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DatasetTab } from '@/pages/data-output/components/data-output-tabs/dataset-tab/dataset-tab.tsx';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { TechnologiesTab } from './technologies-tab/technologies-tab';
import { DataContractsTab } from './data-contracts-tab/data-contracts-tab';

type Props = {
    dataOutputId: string;
    isLoading: boolean;
};

enum TabKeys {
    Datasets = 'datasets',
    Technologies = 'technologies',
    DataContracts = 'contracts'
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
                children: <TechnologiesTab dataOutputId={dataOutputId} />
            },
            {
                label: t('Data contracts'),
                key: TabKeys.DataContracts,
                icon: <FileProtectOutlined />,
                children: <DataContractsTab dataOutputId={dataOutputId} />
            },
        ];
    }, [dataOutputId, t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <Tabs
            defaultActiveKey={TabKeys.Datasets}
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
