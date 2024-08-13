import styles from './platforms-configs.module.scss';
import { PlatformsConfigsTable } from './components/platforms-configs-table/platforms-configs-table.component';

export function PlatformsConfigs() {
    return (
        <div className={styles.container}>
            <PlatformsConfigsTable />
        </div>
    );
}
