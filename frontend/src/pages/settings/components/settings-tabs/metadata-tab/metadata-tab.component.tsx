import { DomainTable } from '../components/domain-table/domain-table.component';
import { EnvironmentTable } from '../components/environment-table/environment-table.component';
import { TagsTable } from '../components/tags-table/tags-table.component';

export function MetadataTab() {
    return (
        <div>
            <TagsTable />
            <DomainTable />
            <EnvironmentTable />
        </div>
    );
}
