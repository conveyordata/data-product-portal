import { DataProductSettingsTable } from '@/pages/settings/components/data-product-settings-table/data-product-settings-table.component';

import { DataProductLifecyclesTable } from '../data-product-lifecycles/components/data-product-lifecycles-table/data-product-lifecycles-table.component';
import { DataProductTypeTable } from './components/data-product-type-table/data-product-type-table.component';
import { DomainTable } from './components/domain-table/domain-table.component';
import { TagsTable } from './components/tags-table/tags-table.component';
import styles from './settings.module.scss';

export function AdditionalSettings() {
    return (
        <div className={styles.container}>
            <DataProductSettingsTable scope={'dataproduct'} />
            <DataProductSettingsTable scope={'dataset'} />
            <DataProductLifecyclesTable />
            <TagsTable />
            <DomainTable />
            <DataProductTypeTable />
        </div>
    );
}
