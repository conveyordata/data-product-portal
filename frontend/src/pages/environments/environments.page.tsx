import { EnvironmentsTable } from './components/environments-table/environments-table.component';
import styles from './environments.module.scss';

export function Environments() {
    return (
        <div className={styles.container}>
            <EnvironmentsTable />
        </div>
    );
}
