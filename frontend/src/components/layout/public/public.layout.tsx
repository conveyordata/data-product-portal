import React, { type ReactNode, useEffect } from 'react';
import { Layout, theme } from 'antd';
import styles from './public.module.scss';
import { useAuth } from 'react-oidc-context';
import { useNavigate } from 'react-router-dom';
import { ApplicationPaths } from '@/types/navigation.ts';

const PublicLayout: React.FC<{ children: ReactNode }> = ({ children }) => {
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
                    {children}
                </div>
            </Layout.Content>
        </Layout>
    );
};

export default PublicLayout;
