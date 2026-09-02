import { DataProductLifecyclesTable } from '../components/data-product-lifecycles-table/data-product-lifecycles-table.component';
import { DomainTable } from '../components/domain-table/domain-table.component';
import { EnvironmentTable } from '../components/environment-table/environment-table.component';
import { TagsTable } from '../components/tags-table/tags-table.component';

export function MetadataTab() {
    return (
        <div>
            <TagsTable />
            <DomainTable />
            <EnvironmentTable />
            <DataProductLifecyclesTable />
        </div>
    );
}
