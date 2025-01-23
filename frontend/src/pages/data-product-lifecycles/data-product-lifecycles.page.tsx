import styles from './data-product-lifecycles.module.scss';
import { DataProductLifecyclesTable } from './components/data-product-lifecycles-table/data-product-lifecycles-table.component';

export function DataProductLifecycles() {
    return (
        <div className={styles.container}>
            <DataProductLifecyclesTable />
        </div>
    );
}
