import { DataProductSettingsTable } from '../components/data-product-settings-table/data-product-settings-table.component';

export function DatasetTab() {
    return (
        <div>
            <DataProductSettingsTable scope={'dataset'} />
        </div>
    );
}
