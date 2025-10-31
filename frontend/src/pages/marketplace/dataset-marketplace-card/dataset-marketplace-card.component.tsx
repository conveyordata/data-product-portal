import {
    BarChartOutlined,
    DatabaseOutlined,
    EyeOutlined,
    NumberOutlined,
    ShareAltOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { Button, Card, Descriptions, type DescriptionsProps, List, Space, Tag, Tooltip, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import { DatasetCard } from '@/components/datasets/dataset-card/dataset-card.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset';
import { createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { DatasetCardTooltip } from './dataset-card-tooltip.component';
import styles from './dataset-marketplace-card.module.scss';

type Props = {
    dataset: DatasetsGetContract[0];
};

export function DatasetMarketplaceCard({ dataset }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();

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
                        ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}
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
                children: <DatasetCardTooltip dataset_id={dataset.id} />,
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
                <Button
                    key="details"
                    style={{ float: 'right', marginRight: '12px' }}
                    type="primary"
                    onClick={() => navigate(createDatasetIdPath(dataset.id))}
                >
                    {t('View Details')}
                </Button>,
            ]}
        >
            <Space direction="vertical" style={{ width: '100%' }} size="small">
                <Typography.Title level={5} style={{ marginBottom: 0 }}>
                    {dataset.name}
                </Typography.Title>
                <div style={{ height: '40px' }}>
                    <Typography.Paragraph ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}>
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
