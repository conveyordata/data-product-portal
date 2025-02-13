import React, { type ReactNode } from 'react';
import { Layout, theme } from 'antd';
import styles from './public.module.scss';

const PublicLayout: React.FC<{ children: ReactNode }> = ({ children }) => {
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

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
