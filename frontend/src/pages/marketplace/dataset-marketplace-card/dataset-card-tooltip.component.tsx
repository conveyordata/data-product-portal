import { List, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { createDataProductIdPath } from '@/types/navigation';
import styles from './dataset-marketplace-card.module.scss';

type Props = {
    dataset_id: string;
};

export function DatasetCardTooltip({ dataset_id }: Props) {
    const { t } = useTranslation();
    const { data: dataset } = useGetDatasetByIdQuery(dataset_id, { skip: !dataset_id });
    if (!dataset) return <Tooltip title={<LoadingSpinner />} />;
    return (
        <Tooltip
            placement="bottom"
            color="white"
            title={
                <List
                    dataSource={dataset.data_product_links}
                    renderItem={(dataProduct) => (
                        <List.Item style={{ margin: 0 }}>
                            <Link to={createDataProductIdPath(dataProduct.data_product_id)} className={styles.link}>
                                {dataProduct.data_product.name}
                            </Link>
                        </List.Item>
                    )}
                />
            }
        >
            {t('{{count}} data products', { count: dataset.data_product_links.length })}
        </Tooltip>
    );
}
