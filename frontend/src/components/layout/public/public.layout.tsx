import { Layout, theme } from 'antd';
import { useEffect } from 'react';
import { useAuth } from 'react-oidc-context';
import { Outlet, useNavigate } from 'react-router';

import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './public.module.scss';

export default function PublicLayout() {
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
}
