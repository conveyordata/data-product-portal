import { DataProductSettingScope } from '@/store/api/services/generated/configurationDataProductSettingsApi.ts';
import { DataProductSettingsTable } from '../components/data-product-settings-table/data-product-settings-table.component';

export function OutputPortTab() {
    return <DataProductSettingsTable scope={DataProductSettingScope.Dataset} />;
}
