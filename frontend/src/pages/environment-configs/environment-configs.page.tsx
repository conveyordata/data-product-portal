import { EnvironmentConfigsTable } from './components/environment-configs-table/environment-configs-table.component';
import styles from './environment-configs.module.scss';

export function EnvironmentConfigs() {
    return (
        <div className={styles.container}>
            <EnvironmentConfigsTable />
        </div>
    );
}
