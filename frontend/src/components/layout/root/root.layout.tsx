import { Layout } from 'antd';
import clsx from 'clsx';
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { Navbar } from '@/components/layout/navbar/navbar.component.tsx';
import { Sidebar } from '@/components/layout/sidebar/sidebar.component.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './root.module.scss';

const RootLayout: React.FC = () => {
    const { pathname } = useLocation();

    const isHome = pathname === ApplicationPaths.Home;
    const layoutChildrenWrapperClasses = clsx(styles.childrenWrapper, {
        [styles.layoutContentHome]: isHome,
    });

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
};

export default RootLayout;
