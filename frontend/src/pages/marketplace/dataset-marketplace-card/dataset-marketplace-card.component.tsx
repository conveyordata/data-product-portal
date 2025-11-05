import {
    BarChartOutlined,
    CheckOutlined,
    DatabaseOutlined,
    EyeOutlined,
    NumberOutlined,
    PlusOutlined,
    ShareAltOutlined,
    ShoppingCartOutlined,
    TeamOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import { Button, Card, Descriptions, type DescriptionsProps, Space, Tag, Tooltip, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useAppDispatch } from '@/store';
import { addDatasetToCart, removeDatasetFromCart, selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset';
import { createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { DatasetCardTooltip } from './dataset-card-tooltip.component';
import styles from './dataset-marketplace-card.module.scss';

type Props = {
    dataset: DatasetsGetContract[0];
};

export function DatasetMarketplaceCard({ dataset }: Props) {
    const { t } = useTranslation();
    const dispatch = useAppDispatch();
    const cartDatasetIds = useSelector(selectCartDatasetIds);

    const toggleCart = (datasetId: string) => {
        if (cartDatasetIds.includes(datasetId)) {
            dispatch(removeDatasetFromCart({ datasetId }));
        } else {
            dispatch(addDatasetToCart({ datasetId }));
        }
    };

    function createCardDetails(dataset: DatasetsGetContract[0]) {
        const items: DescriptionsProps['items'] = [
            {
                key: 'domain',
                label: (
                    <Space>
                        <ShareAltOutlined />
                        {t('Domain')}
                    </Space>
                ),
                children: dataset.domain.name,
            },
            {
                key: 'status',
                label: (
                    <Space>
                        <EyeOutlined />
                        {t('Status')}
                    </Space>
                ),
                children: <Tag color={dataset.lifecycle.color}>{dataset.lifecycle.name}</Tag>,
            },
            {
                key: 'access type',
                label: (
                    <Space>
                        <DatabaseOutlined />
                        {t('Access type')}
                    </Space>
                ),
                children: dataset.access_type,
            },
            {
                key: 'technical assets',
                label: (
                    <Space>
                        <NumberOutlined />
                        {t('Technical Assets')}
                    </Space>
                ),
                span: 2,
                children: dataset.data_output_links.length,
            },
            {
                key: 'data product',
                label: (
                    <Space>
                        <TeamOutlined />
                        {t('Data Product')}
                    </Space>
                ),
                children: (
                    <Typography.Paragraph
                        style={{ height: '44px' }} // To keep 2 rows for the data product height
                        ellipsis={{ rows: 2, tooltip: true }}
                    >
                        <Link to={createDataProductIdPath(dataset.data_product_id)} className={styles.link}>
                            {dataset.data_product_name}
                        </Link>
                    </Typography.Paragraph>
                ),
            },
            {
                key: 'usage',
                label: (
                    <Space>
                        <BarChartOutlined />
                        {t('Usage')}
                    </Space>
                ),
                children: (
                    <DatasetCardTooltip dataset_id={dataset.id} number_of_data_products={dataset.data_product_count} />
                ),
            },
        ];
        return items;
    }
    if (!dataset) return <LoadingSpinner />;
    return (
        <Card
            key={dataset.id}
            styles={{ body: { padding: 12 } }}
            className={styles.marketplaceCardContainer}
            actions={[
                <Tooltip key="details" title={t('View details')}>
                    <Link to={createDatasetIdPath(dataset.id)}>
                        <Button type="text" icon={<UnorderedListOutlined />} />
                    </Link>
                </Tooltip>,
                <Tooltip
                    key="details"
                    title={cartDatasetIds.includes(dataset.id) ? t('Remove from cart') : t('Add to cart')}
                >
                    <Button
                        key="add to cart"
                        type={'text'}
                        size={'middle'}
                        onClick={(e) => {
                            e.preventDefault();
                            toggleCart(dataset.id);
                        }}
                    >
                        {cartDatasetIds.includes(dataset.id) ? (
                            <>
                                <CustomSvgIconLoader
                                    size={'x-small'}
                                    iconComponent={ShoppingCartOutlined}
                                    color={'success'}
                                />
                                <CustomSvgIconLoader size={'x-small'} iconComponent={CheckOutlined} color={'success'} />
                            </>
                        ) : (
                            <>
                                <CustomSvgIconLoader
                                    size={'x-small'}
                                    iconComponent={ShoppingCartOutlined}
                                    color={'primary'}
                                />
                                <CustomSvgIconLoader size={'x-small'} iconComponent={PlusOutlined} color={'primary'} />
                            </>
                        )}
                    </Button>
                </Tooltip>,
            ]}
        >
            <Space direction="vertical" style={{ width: '100%' }} size="small">
                <Typography.Title level={5} style={{ marginBottom: 0 }}>
                    {dataset.name}
                </Typography.Title>
                <div style={{ height: '40px' }}>
                    <Typography.Paragraph ellipsis={{ rows: 2, tooltip: true }}>
                        {dataset.description || 'No description available.'}
                    </Typography.Paragraph>
                </div>
                <div style={{ height: '22px' }}>
                    {dataset.tags?.map((tag) => (
                        <Tag color={tag.rolled_up ? 'red' : 'success'} key={tag.value}>
                            {tag.value}
                        </Tag>
                    ))}
                </div>

                <Descriptions
                    layout="vertical"
                    size={'small'}
                    colon={false}
                    column={2}
                    items={createCardDetails(dataset)}
                />
            </Space>
        </Card>
    );
}
