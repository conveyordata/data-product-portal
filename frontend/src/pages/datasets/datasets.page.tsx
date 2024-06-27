import styles from './datasets.module.scss';
import { DatasetsTable } from '@/pages/datasets/components/datasets-table/datasets-table.component.tsx';

export function Datasets() {
    return (
        <div className={styles.container}>
            <DatasetsTable />
        </div>
    );
}
