import { Flex, Layout, Menu, MenuProps, Space } from 'antd';
import styles from './sidebar.module.scss';
import React from 'react';
import { Link, useMatches } from 'react-router-dom';
import { ApplicationPaths } from '@/types/navigation.ts';
import Icon, { HomeOutlined, SettingOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { SidebarLogo } from '@/components/branding/sidebar-logo/sidebar-logo.tsx';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';

const DataProductIcon = () => <Icon component={dataProductOutlineIcon} />;
const DatasetIcon = () => <Icon component={datasetOutlineIcon} />;

export const Sidebar = () => {
    const matches = useMatches();
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
                label: <Link to={ApplicationPaths.Settings}>{t('Configure')}</Link>,
                icon: React.createElement(SettingOutlined),
                key: ApplicationPaths.Settings,
            },
        ];
    }

    const rootPath =
        matches.map((match) => match.pathname).find((path) => path !== ApplicationPaths.Home) || ApplicationPaths.Home;

    return (
        <Layout.Sider className={styles.sidebarWrapper}>
            <Flex vertical className={styles.sidebarContent}>
                <Space className={styles.logoWrapper}>
                    <Link to={ApplicationPaths.Home}>
                        <SidebarLogo />
                    </Link>
                </Space>
                <Menu theme="dark" mode="vertical" selectedKeys={[rootPath]} items={navigationMenuItems} />
            </Flex>
        </Layout.Sider>
    );
};
