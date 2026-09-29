import { DataProductSettingScope } from '@/store/api/services/generated/configurationDataProductSettingsApi.ts';
import { DataProductSettingsTable } from '../components/data-product-settings-table/data-product-settings-table.component';
import { OutputPortAccessTypesTable } from '../components/output-port-access-types-table/output-port-access-types-table.component';

export function OutputPortTab() {
    return (
        <div>
            <OutputPortAccessTypesTable />
            <DataProductSettingsTable scope={DataProductSettingScope.Dataset} />
        </div>
    );
}
