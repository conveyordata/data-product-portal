import { DataProductSettingScope } from '@/store/api/services/generated/configurationDataProductSettingsApi.ts';
import { DataProductSettingsTable } from '../components/data-product-settings-table/data-product-settings-table.component';
import { OutputPortClassificationsTable } from '../components/output-port-classifications-table/output-port-classifications-table.component';

export function OutputPortTab() {
    return (
        <div>
            <OutputPortClassificationsTable />
            <DataProductSettingsTable scope={DataProductSettingScope.Dataset} />
        </div>
    );
}
