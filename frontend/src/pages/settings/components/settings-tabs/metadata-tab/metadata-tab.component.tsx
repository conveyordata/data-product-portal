import styles from './metadata-tab.module.scss';
import { TagsTable } from '../components/tags-table/tags-table.component';
import { DomainTable } from '../components/domain-table/domain-table.component';
import { DataProductLifecyclesTable } from '../components/data-product-lifecycles-table/data-product-lifecycles-table.component';

export function MetadataTab() {
    return (
        <div>
            <TagsTable />
            <DomainTable />
            <DataProductLifecyclesTable />
        </div>
    );
}
