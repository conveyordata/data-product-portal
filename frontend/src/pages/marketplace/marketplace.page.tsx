import {
    BarChartOutlined,
    DatabaseOutlined,
    EyeOutlined,
    NumberOutlined,
    TeamOutlined,
    ShareAltOutlined,
} from '@ant-design/icons';
import {Button, Card, Descriptions, Divider, Flex, Form, Input, Pagination, Space, Tag, Typography, DescriptionsProps} from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import type {DatasetsGetContract} from '@/types/dataset';
import { createDatasetIdPath } from '@/types/navigation.ts';

function filterDatasets(datasets: DatasetsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return datasets;
    }
    return datasets.filter((dataset) => dataset.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export function Marketplace() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const pageSize = 12;
    const [currentPage, setCurrentPage] = useState(1);
    const { data: datasets = [] } = useGetAllDatasetsQuery();
    const CAPTURE_SEARCH_EVENT_DELAY = 750;
    const [searchTerm, setSearchTerm] = useState('');

    const filteredDatasets = useMemo(() => {
        return filterDatasets(datasets, searchTerm);
    }, [datasets, searchTerm]);
    const paginatedDatasets = useMemo(() => {
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        return filteredDatasets.slice(startIndex, endIndex);
    }, [filteredDatasets, currentPage]);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    const handleSearchChange = (value: string) => {
        setSearchTerm(value);
        setCurrentPage(1); // Reset to first page on search
    };

    useEffect(() => {
        if (searchTerm === undefined || searchTerm === '') return;

        const oldTerm = searchTerm;
        const timeoutId = setTimeout(() => {
            posthog.capture(PosthogEvents.MARKETPLACE_SEARCHED_DATASET, {
                search_term: oldTerm,
            });
        }, CAPTURE_SEARCH_EVENT_DELAY);

        return () => clearTimeout(timeoutId); // clear if searchTerm gets updated beforehand
    }, [searchTerm]);

    const cardMargin = 12;

    function createCardItems(dataset: any) {
        const items : DescriptionsProps['items'] = [
            {
                key: '1',
                label: <Space><ShareAltOutlined /> Domain</Space>,
                children: dataset.domain.name,
            },
            {
                key: '2',
                label: <Space><EyeOutlined /> Status</Space>,
                children: dataset.status,
            },
            {
                key: '3',
                label: <Space><DatabaseOutlined /> Access type</Space>,
                children: dataset.access_type,
            },
            {
                key: '4',
                label: <Space><NumberOutlined /> Technical Asset</Space>,
                span: 2,
                children: dataset.data_output_links.length,
            },
            {
                key: '5',
                label: <Space><TeamOutlined />Data Product</Space>,
                children: <Typography.Paragraph style={{height: '44px'}} // To keep 2 rows for the data product height
                                                ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}>
                    {dataset.data_product_name}
                </Typography.Paragraph>,
            },
            {
                key: '5',
                label: <Space><BarChartOutlined />Usage</Space>,
                children: (dataset.data_product_count === 1
                        ? t('1 data product')
                        : t('{{count}} data products', { count: dataset.data_product_count })),
            },
        ];
        return items;
    }

    return (
        <div>
            <Flex align={'center'} style={{ display: 'flex', gap: 16 }}>
                <Typography.Title level={3}>{t('Marketplace')}</Typography.Title>
                <Form style={{ flex: 1 }}>
                    <Input.Search
                        style={{ height: '40px' }}
                        placeholder={t('Search datasets by name')}
                        value={searchTerm}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        allowClear
                    />
                </Form>
            </Flex>
            <Flex
                wrap="wrap"
                style={{
                    marginTop: '6px',
                    display: 'flex',
                    flexWrap: 'wrap',
                    margin: -cardMargin, // Compensate for the card margin
                }}
            >
                {paginatedDatasets.map((dataset) => (
                    <Card
                        key={dataset.id}
                        styles={{ body: { padding: 12 } }}
                        style={{
                            flex: '1 1 360',
                            marginLeft: 0,
                            margin: cardMargin,
                            width: 360,
                            boxShadow: '0 2px 8px #f0f1f2',
                        }}
                    >
                        <Space direction="vertical" style={{ width: '100%' }} size="small">
                            <div>
                                <Typography.Title level={5} style={{ marginBottom: 0 }}>
                                    {dataset.name}
                                </Typography.Title>
                                <div style={{ height: '40px' }}>
                                    <Typography.Paragraph ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}>
                                        {dataset.description || 'No description available.'}
                                    </Typography.Paragraph>
                                </div>
                                <div style={{ marginTop: 6, height: '22px' }}>
                                    {dataset.tags?.map((tag) => (
                                        <Tag key={tag.value}>{tag.value}</Tag>
                                    ))}
                                </div>
                            </div>

                            <Descriptions layout="vertical" size={"small"} colon={false} column={2} items={createCardItems(dataset)}></Descriptions>

                            <Divider style={{borderColor: '#f0f0f0'}} size='small'/>

                            <Space style={{ float: 'right' }}>
                                {/*<Button icon={<ShoppingCartOutlined />} onClick={() => handleAddToBasket(dataset.id)}>
                                    Add to Cart
                                </Button>*/}
                                <Button type="primary" onClick={() => navigate(createDatasetIdPath(dataset.id))}>
                                    View Details
                                </Button>
                            </Space>
                        </Space>
                    </Card>
                ))}
            </Flex>
            {filteredDatasets.length > pageSize && (
                <div
                    style={{
                        marginTop: 24,
                        display: 'flex',
                        justifyContent: 'flex-end',
                    }}
                >
                    <Pagination
                        current={currentPage}
                        pageSize={pageSize}
                        total={filteredDatasets.length}
                        onChange={handlePageChange}
                        showSizeChanger={false} // Disable page size changer
                    />
                </div>
            )}
        </div>
    );
}
