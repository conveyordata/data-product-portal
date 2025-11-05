import { ShoppingCartOutlined } from '@ant-design/icons';
import { Badge, Button } from 'antd';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import styles from '@/components/layout/navbar/cli-download/cli-download-button.module.scss';
import { selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

export const CartButton = () => {
    const { data: datasets } = useGetAllDatasetsQuery();
    const cartDatasetIds = useSelector(selectCartDatasetIds);
    const cartDatasets = useMemo(() => {
        if (!datasets || cartDatasetIds.length === 0) {
            return [];
        }
        return datasets?.filter((dataset) => cartDatasetIds.includes(dataset.id));
    }, [datasets, cartDatasetIds]);
    return (
        <Badge count={cartDatasets?.length}>
            <Link to={ApplicationPaths.MarketplaceCart}>
                <Button shape={'circle'} className={styles.iconButton} icon={<ShoppingCartOutlined />} />
            </Link>
        </Badge>
    );
};
