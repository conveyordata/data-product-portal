import { UsersTable } from '@/pages/users/components/users-table/users-table.component.tsx';
import styles from './users.module.scss';

export function Users() {
    return (
        <div className={styles.container}>
            <UsersTable />
        </div>
    );
}
