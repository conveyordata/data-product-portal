import styles from './roles.module.scss';
import { RolesTable } from '@/pages/roles/components/roles-table.component.tsx';
import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

export function RoleConfiguration() {
    const { t } = useTranslation();

    return (
        <div className={styles.container}>
            <Typography.Title level={2}>{t('Manage Roles')}</Typography.Title>

            <RolesTable />
        </div>
    );
}
