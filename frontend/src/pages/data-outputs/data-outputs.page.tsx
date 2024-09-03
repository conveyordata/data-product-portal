import { DataOutputsTable } from '@/pages/data-outputs/components/data-outputs-table/data-outputs-table.component';
import styles from './data-outputs.module.scss';

export function DataOutputs() {
    return (
        <div className={styles.container}>
            <DataOutputsTable />
        </div>
    );
}
