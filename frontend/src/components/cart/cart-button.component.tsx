import { ShoppingCartOutlined } from '@ant-design/icons';
import { Badge, Button, Flex, Popover } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import { CartOverview } from '@/components/cart/cart-overview.component.tsx';
import styles from '@/components/layout/navbar/cli-download/cli-download-button.module.scss';
import { useAppDispatch } from '@/store';
import { clearCart, selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

export const CartButton = () => {
    const { t } = useTranslation();
    const dispatch = useAppDispatch();
    const { data: datasets, isFetching } = useGetAllDatasetsQuery();
    const cartDatasetIds = useSelector(selectCartDatasetIds);
    const cartDatasets = useMemo(() => {
        if (!datasets || cartDatasetIds.length === 0) {
            return [];
        }
        return datasets?.filter((dataset) => cartDatasetIds.includes(dataset.id));
    }, [datasets, cartDatasetIds]);
    return (
        <Popover
            content={
                <div style={{ width: '500px' }}>
                    <CartOverview
                        cartDatasets={cartDatasets}
                        loading={isFetching}
                        footer={
                            <Flex justify={'flex-end'} gap={'small'}>
                                <Button
                                    onClick={() => {
                                        dispatch(clearCart());
                                    }}
                                    disabled={cartDatasets.length === 0}
                                >
                                    {t('Clear cart')}
                                </Button>
                                <Link to={ApplicationPaths.MarketplaceCart}>
                                    <Button type="primary" disabled={cartDatasets.length === 0}>
                                        {t('Checkout')}
                                    </Button>
                                </Link>
                            </Flex>
                        }
                    />
                </div>
            }
            trigger={'hover'}
            placement="bottom"
        >
            <Badge count={cartDatasets?.length}>
                <Link to={ApplicationPaths.MarketplaceCart}>
                    <Button shape={'circle'} className={styles.iconButton} icon={<ShoppingCartOutlined />} />
                </Link>
            </Badge>
        </Popover>
    );
};
