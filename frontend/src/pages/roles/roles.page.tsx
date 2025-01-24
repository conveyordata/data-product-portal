import styles from './roles.module.scss';
import { RolesTable } from '@/pages/roles/components/roles-table.component.tsx';

export function RoleConfiguration() {
    return (
        <div className={styles.container}>
            <RolesTable />
        </div>
    );
}
