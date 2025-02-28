import { Tabs } from 'antd';
import { ReactNode, useMemo } from 'react';
import styles from './settings-tabs.module.scss';
import { useTranslation } from 'react-i18next';
import { GeneralTab } from './general-tab/general-tab.component';
import { DataProductTab } from './data-product-tab/data-product-tab.component';
import { RolesTab } from './roles-tab/roles-tab.component';
import { MetadataTab } from './metadata-tab/metadata-tab.component';
import { PlatformTab } from './platform-tab/platform-tab.component';
import { DatasetTab } from './dataset-tab/dataset-tab.component';
import { DataOutputTab } from './data-output-tab/data-output-tab.component';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import chipIcon from '@/assets/icons/chip-icon.svg?react';
import Icon, { InfoCircleOutlined, SettingOutlined, TeamOutlined } from '@ant-design/icons';

export enum TabKeys {
    General = 'general',
    DataProduct = 'data-product',
    DataSet = 'dataset',
    DataOutput = 'data-output',
    Platform = 'platform',
    Roles = 'roles',
    Metadata = 'metadata',
}

type Tab = {
    label: string;
    key: TabKeys;
    icon?: ReactNode;
    children: ReactNode;
    hidden?: boolean;
};

export function SettingsTabs() {
    const { t } = useTranslation();

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('General'),
                key: TabKeys.General,
                children: <GeneralTab />,
                icon: <SettingOutlined />,
            },
            {
                label: t('Data Product'),
                key: TabKeys.DataProduct,
                children: <DataProductTab />,
                icon: <Icon component={dataProductOutlineIcon} />,
            },
            {
                label: t('Dataset'),
                key: TabKeys.DataSet,
                children: <DatasetTab />,
                icon: <Icon component={datasetOutlineIcon} />,
            },
            {
                label: t('Data Output'),
                key: TabKeys.DataOutput,
                children: <DataOutputTab />,
                icon: <Icon component={dataOutputOutlineIcon} />,
                hidden: true,
            },
            {
                label: t('Metadata'),
                key: TabKeys.Metadata,
                children: <MetadataTab />,
                icon: <InfoCircleOutlined />,
            },
            {
                label: t('Platform'),
                key: TabKeys.Platform,
                children: <PlatformTab />,
                icon: <Icon component={chipIcon} />,
                hidden: true,
            },
            {
                label: t('Roles'),
                key: TabKeys.Roles,
                children: <RolesTab />,
                icon: <TeamOutlined />,
                hidden: true,
            },
        ];
    }, [t]);

    return (
        <Tabs
            defaultActiveKey={TabKeys.General}
            items={tabs
                .filter((tab) => !tab.hidden)
                .map(({ key, label, icon, children }) => {
                    return {
                        label,
                        key,
                        children,
                        icon,
                        className: styles.tabPane,
                    };
                })}
            size={'middle'}
            rootClassName={styles.tabContainer}
        />
    );
}
