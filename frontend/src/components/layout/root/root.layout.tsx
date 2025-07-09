import { Layout } from 'antd';
import clsx from 'clsx';
import { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router';
import { Navbar } from '@/components/layout/navbar/navbar.component.tsx';
import { Sidebar } from '@/components/layout/sidebar/sidebar.component.tsx';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './root.module.scss';

export default function RootLayout() {
    const { pathname } = useLocation();

    const isHome = pathname === ApplicationPaths.Home;
    const layoutChildrenWrapperClasses = clsx(styles.childrenWrapper, {
        [styles.layoutContentHome]: isHome,
    });

    useEffect(() => {
        // general capture
        let abstract_pathname = pathname;

        // if the pathname ends with a UUID, replace it with an asterisk.
        const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        if (pathname.length >= 36) {
            const potentialUUID = pathname.slice(-36);
            if (UUID_REGEX.test(potentialUUID)) abstract_pathname = pathname.slice(0, -36) + '*';
        }

        posthog.capture(PosthogEvents.PATHNAME_CHANGED, { pathname: abstract_pathname });

        // explicit captures for sidebar/main pages
        switch (pathname) {
            case ApplicationPaths.Home:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_HOMEPAGE);
                break;
            case ApplicationPaths.DataProducts:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_DATA_PRODUCTS);
                break;
            case ApplicationPaths.Datasets:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_MARKETPLACE);
                break;
            case ApplicationPaths.Explorer:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_EXPLORER);
                break;
            case ApplicationPaths.People:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_PEOPLE);
                break;
            case ApplicationPaths.AuditLogs:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_AUDIT_LOGS);
                break;
            case ApplicationPaths.Settings:
                posthog.capture(PosthogEvents.PATHNAME_CHANGED_SETTINGS);
                break;
            default:
        }
    }, [pathname]);

    return (
        <Layout className={styles.layoutWrapper} hasSider>
            <Sidebar />
            <Layout>
                <Navbar />
                <Layout.Content className={styles.layoutContent}>
                    <div className={layoutChildrenWrapperClasses}>
                        <Outlet />
                    </div>
                </Layout.Content>
            </Layout>
        </Layout>
    );
}
