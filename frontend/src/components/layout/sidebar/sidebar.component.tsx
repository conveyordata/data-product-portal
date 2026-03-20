import {
    CompassOutlined,
    FileSearchOutlined,
    HomeOutlined,
    ProductOutlined,
    SettingOutlined,
    ShopOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { Flex, Layout, Menu, type MenuProps, Space } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useMatches } from 'react-router';
import { SidebarLogo } from '@/components/branding/sidebar-logo/sidebar-logo.tsx';
import { ProductLogo } from '@/components/icons';
import AnimatedWizard from '@/components/wizard/wizard.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetVersionQuery } from '@/store/api/services/generated/versionApi.ts';
import { selectWizardEnabled } from '@/store/features/wizard/wizard-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './sidebar.module.scss';

export const Sidebar = () => {
    const { t } = useTranslation();
    const matches = useMatches();
    const { data: version } = useGetVersionQuery();

    const showWizard = useSelector(selectWizardEnabled);

    let navigationMenuItems: MenuProps['items'] = [
        {
            label: <Link to={ApplicationPaths.Home}>{t('Home')}</Link>,
            icon: <HomeOutlined />,
            key: ApplicationPaths.Home,
        },
        {
            label: <Link to={ApplicationPaths.Studio}>{t('Product Studio')}</Link>,
            icon: <ProductOutlined />,
            key: ApplicationPaths.Studio,
        },
        {
            label: <Link to={ApplicationPaths.Marketplace}>{t('Marketplace')}</Link>,
            icon: <ShopOutlined />,
            key: ApplicationPaths.Marketplace,
        },
        {
            label: <Link to={ApplicationPaths.Explorer}>{t('Explorer')}</Link>,
            icon: <CompassOutlined />,
            key: ApplicationPaths.Explorer,
        },
        {
            label: <Link to={ApplicationPaths.People}>{t('People')}</Link>,
            icon: <TeamOutlined />,
            key: ApplicationPaths.People,
        },
        {
            label: (
                <a href={'https://docs.dataproductportal.com/docs/intro'} target="_blank" rel="noopener noreferrer">
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
            <Flex vertical justify="space-between" style={{height: "100%"}}>
                <div>
                    <Flex className={styles.logoContainer}>
                        <ProductLogo
                            className={clsx([styles.defaultIcon, styles.sidebarContent, styles.iconWrapper])}
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
                </div>

                {showWizard && (
                    <Flex justify="center" style={{ width: '100%', paddingBottom: '16px' }}>
                            <AnimatedWizard size={200} />
                    </Flex>
                )}
            </Flex>
        </Layout.Sider>
    );
};
