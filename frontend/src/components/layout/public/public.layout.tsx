import { Layout, theme } from 'antd';
import React, { useEffect } from 'react';
import { useAuth } from 'react-oidc-context';
import { Outlet, useNavigate } from 'react-router-dom';

import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './public.module.scss';

const PublicLayout: React.FC = () => {
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    const { isAuthenticated } = useAuth();
    const redirect = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            redirect(ApplicationPaths.Home);
        }
    }, [isAuthenticated, redirect]);

    return (
        <Layout className={styles.layoutWrapper} hasSider>
            <Layout.Content className={styles.layoutContent}>
                <div
                    className={styles.childrenWrapper}
                    style={{
                        background: colorBgContainer,
                        borderRadius: borderRadiusLG,
                    }}
                >
                    <Outlet />
                </div>
            </Layout.Content>
        </Layout>
    );
};

export default PublicLayout;
