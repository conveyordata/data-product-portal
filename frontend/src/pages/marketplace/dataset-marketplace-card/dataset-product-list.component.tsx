import { List } from 'antd';
import { useMemo } from 'react';
import { Link } from 'react-router';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { createDataProductIdPath } from '@/types/navigation';
import styles from './dataset-marketplace-card.module.scss';

type Props = {
    dataset_id: string;
};

export function DatasetProductList({ dataset_id }: Props) {
    const { data: dataset } = useGetDatasetByIdQuery(dataset_id, { skip: !dataset_id });

    const filteredProductLinks = useMemo(() => {
        return dataset?.data_product_links.filter((link) => link.status === 'approved') || [];
    }, [dataset]);
    if (!dataset) return <LoadingSpinner />;
    if (filteredProductLinks.length === 0) return null;
    return (
        <List
            dataSource={filteredProductLinks}
            renderItem={(dataProduct) => (
                <List.Item style={{ margin: 0 }}>
                    <Link to={createDataProductIdPath(dataProduct.data_product_id)} className={styles.link}>
                        {dataProduct.data_product.name}
                    </Link>
                </List.Item>
            )}
        />
    );
}
