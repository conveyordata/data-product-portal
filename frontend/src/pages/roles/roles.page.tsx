import styles from './roles.module.scss';
import { RolesTable } from '@/pages/roles/components/roles-table.component.tsx';
import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { MenuProps } from 'antd';
import { Menu } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { useState } from 'react';

const { Paragraph } = Typography;

type MenuItem = Required<MenuProps>['items'][number];

export function RoleConfiguration() {
    const { t } = useTranslation();
    const [current, setCurrent] = useState('global');

    const items: MenuItem[] = [
        {
            label: t('Global'),
            key: 'global',
            icon: <GlobalOutlined />,
        },
        {
            label: t('Data Products'),
            key: 'data_products',
            icon: <GlobalOutlined />,
        },
        {
            label: t('Datasets'),
            key: 'datasets',
            icon: <GlobalOutlined />,
        },
    ];

    const onClick: MenuProps['onClick'] = (e) => {
        setCurrent(e.key);
    };

    return (
        <div className={styles.container}>
            <Typography.Title level={2}>{t('Manage Roles')}</Typography.Title>
            <Paragraph>{t('Roles are reusable sets of permissions.')}</Paragraph>

            <Menu onClick={onClick} selectedKeys={[current]} mode="horizontal" items={items} />
            <RolesTable />
        </div>
    );
}
