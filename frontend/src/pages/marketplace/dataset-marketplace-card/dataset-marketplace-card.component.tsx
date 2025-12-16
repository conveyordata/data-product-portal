import {
    BarChartOutlined,
    CheckOutlined,
    DatabaseOutlined,
    EyeOutlined,
    NumberOutlined,
    PlusOutlined,
    QuestionCircleOutlined,
    ShareAltOutlined,
    ShoppingCartOutlined,
    TeamOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import {
    Button,
    Card,
    Descriptions,
    type DescriptionsProps,
    Flex,
    Popover,
    Space,
    Tag,
    Tooltip,
    Typography,
} from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { DatasetReason } from '@/pages/marketplace/dataset-marketplace-card/dataset-reason.tsx';
import { useAppDispatch } from '@/store';
import { addDatasetToCart, removeDatasetFromCart, selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset';
import { createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { DatasetCardTooltip } from './dataset-card-tooltip.component';
import styles from './dataset-marketplace-card.module.scss';

type Props = {
    dataset: DatasetsGetContract[0];
    query: string;
};

export function DatasetMarketplaceCard({ dataset, query }: Props) {
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

    const [open, setOpen] = useState(false);
    const hide = () => {
        setOpen(false);
    };
    const handleOpenChange = (newOpen: boolean) => {
        console.log('clicked');
        setOpen(newOpen);
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
                children: <Typography.Text ellipsis={{ tooltip: true }}>{dataset.domain.name}</Typography.Text>,
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
                children: <Typography.Text ellipsis={{ tooltip: true }}>{dataset.access_type}</Typography.Text>,
            },
            {
                key: 'technical assets',
                label: (
                    <Space>
                        <NumberOutlined />
                        {t('Technical Assets')}
                    </Space>
                ),
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
        <Tooltip title={t('Found what you are looking for, use the add to cart button below!')}>
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
                                    <CustomSvgIconLoader
                                        size={'x-small'}
                                        iconComponent={CheckOutlined}
                                        color={'success'}
                                    />
                                </>
                            ) : (
                                <>
                                    <CustomSvgIconLoader
                                        size={'x-small'}
                                        iconComponent={ShoppingCartOutlined}
                                        color={'primary'}
                                    />
                                    <CustomSvgIconLoader
                                        size={'x-small'}
                                        iconComponent={PlusOutlined}
                                        color={'primary'}
                                    />
                                </>
                            )}
                        </Button>
                    </Tooltip>,
                ]}
            >
                <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                    <Flex justify="space-between" align="center">
                        <Link to={createDatasetIdPath(dataset.id)}>
                            <Typography.Title level={5} style={{ marginBottom: 0 }}>
                                {dataset.name}
                            </Typography.Title>
                        </Link>
                        {/* Make the color graded based on the ranking */}
                        {dataset.rank && (
                            <Typography.Title
                                level={3}
                                style={{
                                    marginBottom: 0,
                                    color: dataset.rank > 0.75 ? 'green' : dataset.rank > 0.5 ? 'orange' : 'red',
                                }}
                            >
                                {(dataset.rank * 100).toFixed(0)} %
                            </Typography.Title>
                        )}
                        {dataset.reason ? (
                            <Popover
                                content={<Button onClick={hide}>Close</Button>}
                                title={dataset.reason}
                                open={open}
                                onOpenChange={handleOpenChange}
                                trigger="click"
                            >
                                <QuestionCircleOutlined className={styles.questionTooltip} />
                            </Popover>
                        ) : (
                            <Popover
                                content={<Button onClick={hide}>Close</Button>}
                                title={<DatasetReason dataset_id={dataset.id} query={query} />}
                                open={open}
                                onOpenChange={handleOpenChange}
                                trigger="click"
                            >
                                <QuestionCircleOutlined className={styles.questionTooltip} />
                            </Popover>
                        )}
                    </Flex>
                    <Typography.Paragraph
                        ellipsis={{ rows: 2, tooltip: true }}
                        style={{ height: '44px', marginBottom: 0 }}
                    >
                        {dataset.description || 'No description available.'}
                    </Typography.Paragraph>
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
        </Tooltip>
    );
}
