import Icon, { InfoCircleOutlined, SettingOutlined, TeamOutlined } from '@ant-design/icons';
import { Tabs } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import chipIcon from '@/assets/icons/chip-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { useTabParam } from '@/hooks/use-tab-param.tsx';
import { DataOutputTab } from './data-output-tab/data-output-tab.component';
import { DataProductTab } from './data-product-tab/data-product-tab.component';
import { DatasetTab } from './dataset-tab/dataset-tab.component';
import { GeneralTab } from './general-tab/general-tab.component';
import { MetadataTab } from './metadata-tab/metadata-tab.component';
import { PlatformTab } from './platform-tab/platform-tab.component';
import { RolesTab } from './roles-tab/roles-tab.component';
import styles from './settings-tabs.module.scss';

enum TabKeys {
    General = 'general',
    DataProduct = 'data-product',
    Dataset = 'dataset',
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
    const { activeTab, onTabChange } = useTabParam(TabKeys.General, Object.values(TabKeys));

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
                label: t('Output Port'),
                key: TabKeys.Dataset,
                children: <DatasetTab />,
                icon: <Icon component={datasetOutlineIcon} />,
            },
            {
                label: t('Technical Asset'),
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
            },
        ];
    }, [t]);

    return (
        <Tabs
            activeKey={activeTab}
            onChange={onTabChange}
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
