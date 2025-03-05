import { DataProductSettingsTable } from '../components/data-product-settings-table/data-product-settings-table.component.tsx';
import { DataProductTypeTable } from '../components/data-product-type-table/data-product-type-table.component.tsx';

export function DataProductTab() {
    return (
        <div>
            <DataProductSettingsTable scope={'dataproduct'} />
            <DataProductTypeTable />
        </div>
    );
}
