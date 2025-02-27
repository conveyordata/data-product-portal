import styles from './data-product-tab.module.scss';
import { useTranslation } from 'react-i18next';
import { DataProductSettingsTable } from '../components/data-product-settings-table/data-product-settings-table.component.tsx';
import { DataProductLifecyclesTable } from '../components/data-product-lifecycles-table/data-product-lifecycles-table.component.tsx';
export function DataProductTab() {
    return (
        <div>
            <DataProductSettingsTable scope={'dataproduct'} />
            <DataProductLifecyclesTable />
        </div>
    );
}
