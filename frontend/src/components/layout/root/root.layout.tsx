import { Layout } from 'antd';
import clsx from 'clsx';
import { Outlet, useLocation } from 'react-router';

import { Navbar } from '@/components/layout/navbar/navbar.component.tsx';
import { Sidebar } from '@/components/layout/sidebar/sidebar.component.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './root.module.scss';
import { PosthogEvents } from '@/constants/posthog.constants';
import posthog from '@/config/posthog-config';
import { useEffect } from 'react';

export default function RootLayout() {
    const { pathname } = useLocation();

    const isHome = pathname === ApplicationPaths.Home;
    const layoutChildrenWrapperClasses = clsx(styles.childrenWrapper, {
        [styles.layoutContentHome]: isHome,
    });

    useEffect(() => {
        posthog.capture(PosthogEvents.PATHNAME_CHANGED, {pathname: pathname});
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
