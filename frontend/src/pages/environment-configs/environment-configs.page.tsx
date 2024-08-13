import styles from './environment-configs.module.scss';
import { EnvironmentConfigsTable } from './components/environment-configs-table/environment-configs-table.component';
export function EnvironmentConfigs() {
    return (
        <div className={styles.container}>
            <EnvironmentConfigsTable />
        </div>
    );
}
