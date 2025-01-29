import { DataProductSettingsTable } from '@/pages/data-product-settings/components/data-product-settings-table/data-product-settings-table.component.tsx';
import styles from './data-product-settings.module.scss';
import { DataProductLifecyclesTable } from '../data-product-lifecycles/components/data-product-lifecycles-table/data-product-lifecycles-table.component';

export function DataProductSettings() {
    return (
        <div className={styles.container}>
            <DataProductSettingsTable />
            <DataProductLifecyclesTable />
        </div>
    );
}
