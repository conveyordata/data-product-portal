import { DataProductSettingsTable } from '@/pages/data-product-settings/components/data-product-settings-table/data-product-settings-table.component.tsx';
import styles from './data-product-settings.module.scss';

export function DataProductSettings() {
    return (
        <div className={styles.container}>
            <DataProductSettingsTable />
        </div>
    );
}
