import { Flex, Layout, Menu, MenuProps, Space } from 'antd';
import styles from './sidebar.module.scss';
import React from 'react';
import { Link, useMatches } from 'react-router-dom';
import { ApplicationPaths } from '@/types/navigation.ts';
import Icon, { HomeOutlined, SettingOutlined, UnorderedListOutlined, BranchesOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { SidebarLogo } from '@/components/branding/sidebar-logo/sidebar-logo.tsx';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetVersionQuery } from '@/store/features/version/version-api-slice';
import clsx from 'clsx';
import logo from '@/assets/icons/logo.svg?react';

const DataProductIcon = () => <Icon component={dataProductOutlineIcon} />;
const DatasetIcon = () => <Icon component={datasetOutlineIcon} />;

export const Sidebar = () => {
    const matches = useMatches();
    const { data: version } = useGetVersionQuery();
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);

    let navigationMenuItems: MenuProps['items'] = [
        {
            label: <Link to={ApplicationPaths.Home}>{t('Home')}</Link>,
            icon: React.createElement(HomeOutlined),
            key: ApplicationPaths.Home,
        },
        {
            label: <Link to={ApplicationPaths.DataProducts}>{t('Data Products')}</Link>,
            icon: React.createElement(DataProductIcon),
            key: ApplicationPaths.DataProducts,
        },
        {
            label: <Link to={ApplicationPaths.Datasets}>{t('Datasets')}</Link>,
            icon: React.createElement(DatasetIcon),
            key: ApplicationPaths.Datasets,
        },
        {
            label: <Link to={ApplicationPaths.AuditLogs}>{t('Audit Logs')}</Link>,
            icon: React.createElement(UnorderedListOutlined),
            key: ApplicationPaths.AuditLogs,
        },
    ];

    if (currentUser?.is_admin) {
        navigationMenuItems = [
            ...navigationMenuItems,
            {
                label: t('Configure'),
                icon: React.createElement(SettingOutlined),
                key: 'Configure',
                children: [
                    // {
                    //     key: ApplicationPaths.PlatformsConfigs,
                    //     label: (
                    //         <span className={styles.subMenuTitle}>
                    //             <Link to={ApplicationPaths.PlatformsConfigs}>{t('Platforms Configurations')}</Link>
                    //         </span>
                    //     ),
                    // },
                    // {
                    //     key: ApplicationPaths.Environments,
                    //     label: (
                    //         <span className={styles.subMenuTitle}>
                    //             <Link to={ApplicationPaths.Environments}>{t('Environments')}</Link>
                    //         </span>
                    //     ),
                    // },
                    {
                        key: ApplicationPaths.DataProductSettings,
                        label: <Link to={ApplicationPaths.DataProductSettings}>{t('Data Product Settings')}</Link>,
                        icon: React.createElement(SettingOutlined),
                    },
                    {
                        key: ApplicationPaths.DataProductLifecycles,
                        label: <Link to={ApplicationPaths.DataProductLifecycles}>{t('Data Product Lifecycles')}</Link>,
                        icon: React.createElement(BranchesOutlined),
                    },
                ],
            },
        ];
    }

    const rootPath =
        matches.map((match) => match.pathname).find((path) => path !== ApplicationPaths.Home) || ApplicationPaths.Home;

    return (
        <Layout.Sider className={styles.sidebarWrapper}>
            <Flex className={styles.logoContainer}>
                <Icon
                    className={clsx([styles.defaultIcon, styles.sidebarContent, styles.iconWrapper])}
                    component={logo}
                />
                <Flex vertical className={styles.sidebarContent}>
                    <Space className={styles.logoWrapper}>
                        <Link to={ApplicationPaths.Home}>
                            <SidebarLogo />
                            {version ? version.version : ''}
                        </Link>
                    </Space>
                </Flex>
            </Flex>
            <Menu theme="dark" mode="vertical" selectedKeys={[rootPath]} items={navigationMenuItems} />
        </Layout.Sider>
    );
};
