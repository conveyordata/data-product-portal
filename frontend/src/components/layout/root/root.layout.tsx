import React, { type ReactNode } from 'react';
import { Layout } from 'antd';
import { useLocation } from 'react-router-dom';
import styles from './root.module.scss';
import { Sidebar } from '@/components/layout/sidebar/sidebar.component.tsx';
import { Navbar } from '@/components/layout/navbar/navbar.component.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';
import clsx from 'clsx';

const RootLayout: React.FC<{ children: ReactNode }> = ({ children }) => {
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
                    <div className={layoutChildrenWrapperClasses}>{children}</div>
                </Layout.Content>
            </Layout>
        </Layout>
    );
};

export default RootLayout;
