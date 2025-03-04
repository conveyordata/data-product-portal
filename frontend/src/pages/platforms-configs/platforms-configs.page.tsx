import { PlatformsConfigsTable } from './components/platforms-configs-table/platforms-configs-table.component';
import styles from './platforms-configs.module.scss';

export function PlatformsConfigs() {
    return (
        <div className={styles.container}>
            <PlatformsConfigsTable />
        </div>
    );
}
