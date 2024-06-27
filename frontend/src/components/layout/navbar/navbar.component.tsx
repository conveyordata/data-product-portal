import { Layout, Space } from 'antd';
import { Breadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumbs.component.tsx';
import { UserMenu } from '@/components/layout/navbar/user-menu/user-menu.component.tsx';
import styles from './navbar.module.scss';

export const Navbar = () => {
    return (
        <Layout.Header className={styles.header}>
            <Space className={styles.headerContent}>
                <Breadcrumbs />
                <UserMenu />
            </Space>
        </Layout.Header>
    );
};
