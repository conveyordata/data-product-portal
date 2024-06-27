import { DataProductsTable } from '@/pages/data-products/components/data-products-table/data-products-table.component.tsx';
import styles from './data-products.module.scss';

export function DataProducts() {
    return (
        <div className={styles.container}>
            <DataProductsTable />
        </div>
    );
}
