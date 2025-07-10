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
        // if the pathname contains a UUID, replace it.
        const UUID_REGEX = /[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}/gi;
        posthog.capture(PosthogEvents.PATHNAME_CHANGED, {
            pathname: pathname.replace(UUID_REGEX, '{uuid}'),
        });

        // explicit captures for sidebar/main pages
        const changed_event = (() => {
            switch (pathname) {
                case ApplicationPaths.Home:
                    return PosthogEvents.PATHNAME_CHANGED_HOMEPAGE;
                case ApplicationPaths.DataProducts:
                    return PosthogEvents.PATHNAME_CHANGED_DATA_PRODUCTS;
                case ApplicationPaths.Datasets:
                    return PosthogEvents.PATHNAME_CHANGED_MARKETPLACE;
                case ApplicationPaths.Explorer:
                    return PosthogEvents.PATHNAME_CHANGED_EXPLORER;
                case ApplicationPaths.People:
                    return PosthogEvents.PATHNAME_CHANGED_PEOPLE;
                case ApplicationPaths.AuditLogs:
                    return PosthogEvents.PATHNAME_CHANGED_AUDIT_LOGS;
                case ApplicationPaths.Settings:
                    return PosthogEvents.PATHNAME_CHANGED_SETTINGS;
                default:
                    return undefined;
            }
        })();
        
        if (changed_event) posthog.capture(changed_event);

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
