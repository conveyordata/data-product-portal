import { DataProductSettingsTable } from '@/pages/settings/components/data-product-settings-table/data-product-settings-table.component';
import styles from './settings.module.scss';
import { DataProductLifecyclesTable } from '../data-product-lifecycles/components/data-product-lifecycles-table/data-product-lifecycles-table.component';
import { TagsTable } from './components/tags-table/tags-table.component';
import { BussinesAreaTable } from './components/business-area-table/business-area-table.component';
import { DataProductTypeTable } from './components/data-product-type-table/data-product-type-table.component';

export function AdditionalSettings() {
    return (
        <div className={styles.container}>
            <DataProductSettingsTable scope={'dataproduct'} />
            <DataProductSettingsTable scope={'dataset'} />
            <DataProductLifecyclesTable />
            <TagsTable />
            <BussinesAreaTable />
            <DataProductTypeTable />
        </div>
    );
}
