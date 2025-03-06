import { HomeOutlined, SettingOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { Flex, Layout, Menu, type MenuProps, Space } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useMatches } from 'react-router';

import { SidebarLogo } from '@/components/branding/sidebar-logo/sidebar-logo.tsx';
import { DataProductOutlined, DatasetOutlined, ProductLogo } from '@/components/icons';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetVersionQuery } from '@/store/features/version/version-api-slice';
import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './sidebar.module.scss';

export const Sidebar = () => {
    const matches = useMatches();
    const { data: version } = useGetVersionQuery();
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);

    let navigationMenuItems: MenuProps['items'] = [
        {
            label: <Link to={ApplicationPaths.Home}>{t('Home')}</Link>,
            icon: <HomeOutlined />,
            key: ApplicationPaths.Home,
        },
        {
            label: <Link to={ApplicationPaths.DataProducts}>{t('Data Products')}</Link>,
            icon: <DataProductOutlined />,
            key: ApplicationPaths.DataProducts,
        },
        {
            label: <Link to={ApplicationPaths.Datasets}>{t('Marketplace')}</Link>,
            icon: <DatasetOutlined />,
            key: ApplicationPaths.Datasets,
        },
        {
            label: <Link to={ApplicationPaths.AuditLogs}>{t('Audit Logs')}</Link>,
            icon: <UnorderedListOutlined />,
            key: ApplicationPaths.AuditLogs,
        },
    ];

    if (currentUser?.is_admin) {
        navigationMenuItems = [
            ...navigationMenuItems,
            {
                label: t('Configure'),
                icon: <SettingOutlined />,
                key: 'Configure',
                children: [
                    {
                        key: ApplicationPaths.AdditionalSettings,
                        label: <Link to={ApplicationPaths.AdditionalSettings}>{t('Additional Settings')}</Link>,
                        icon: <SettingOutlined />,
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
                <ProductLogo className={clsx([styles.defaultIcon, styles.sidebarContent, styles.iconWrapper])} />
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
