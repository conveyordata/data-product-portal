import { DatasetsTable } from '@/pages/datasets/components/datasets-table/datasets-table.component.tsx';

import styles from './datasets.module.scss';

export function Datasets() {
    return (
        <div className={styles.container}>
            <DatasetsTable />
        </div>
    );
}
