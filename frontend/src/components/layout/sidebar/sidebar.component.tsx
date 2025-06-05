import {
    CompassOutlined,
    FileSearchOutlined,
    HomeOutlined,
    SettingOutlined,
    TeamOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import { Flex, Layout, Menu, type MenuProps, Space } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';
import { Link, useMatches } from 'react-router';

import { SidebarLogo } from '@/components/branding/sidebar-logo/sidebar-logo.tsx';
import { DataProductOutlined, DatasetOutlined, ProductLogo } from '@/components/icons';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetVersionQuery } from '@/store/features/version/version-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './sidebar.module.scss';

export const Sidebar = () => {
    const matches = useMatches();
    const { data: version } = useGetVersionQuery();
    const { t } = useTranslation();

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
            label: <Link to={ApplicationPaths.Users}>{t('Users')}</Link>,
            icon: <TeamOutlined />,
            key: ApplicationPaths.Users,
        },
        {
            label: <Link to={ApplicationPaths.AuditLogs}>{t('Audit Logs')}</Link>,
            icon: <UnorderedListOutlined />,
            key: ApplicationPaths.AuditLogs,
        },
        {
            label: <Link to={ApplicationPaths.Explorer}>{t('Explorer')}</Link>,
            icon: <CompassOutlined />,
            key: ApplicationPaths.Explorer,
        },
        {
            label: (
                <a
                    href={`https://d33vpinjygaq6n.cloudfront.net/docs/${version?.version.split('.').slice(0, 2).join('.')}.x/intro`}
                    target="_blank"
                >
                    {t('Documentation')}
                </a>
            ),
            icon: <FileSearchOutlined />,
            key: ApplicationPaths.Documentation,
        },
    ];

    const { data: access } = useCheckAccessQuery({
        action: AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION,
    });
    const canAccessSettings = access?.allowed ?? false;

    if (canAccessSettings) {
        navigationMenuItems = [
            ...navigationMenuItems,
            {
                label: <Link to={ApplicationPaths.Settings}>{t('Settings')}</Link>,
                icon: <SettingOutlined />,
                key: 'Settings',
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
