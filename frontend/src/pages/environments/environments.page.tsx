import styles from './environments.module.scss';
import { EnvironmentsTable } from './components/environments-table/environments-table.component';

export function Environments() {
    return (
        <div className={styles.container}>
            <EnvironmentsTable />
        </div>
    );
}
