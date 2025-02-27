import styles from './metadata-tab.module.scss';
import { TagsTable } from '../components/tags-table/tags-table.component';
import { DomainTable } from '../components/domain-table/domain-table.component';
import { DataProductTypeTable } from '../components/data-product-type-table/data-product-type-table.component';

export function MetadataTab() {
    return (
        <div>
            <TagsTable />
            <DomainTable />
            <DataProductTypeTable />
        </div>
    );
}
