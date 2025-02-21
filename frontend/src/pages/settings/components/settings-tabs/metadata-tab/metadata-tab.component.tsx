import styles from './metadata-tab.module.scss';
import { TagsTable } from '../components/tags-table/tags-table.component';
import { BussinesAreaTable } from '../components/business-area-table/business-area-table.component';
import { DataProductTypeTable } from '../components/data-product-type-table/data-product-type-table.component';

export function MetadataTab() {
    return (
        <div>
            <TagsTable />
            <BussinesAreaTable />
            <DataProductTypeTable />
        </div>
    );
}
