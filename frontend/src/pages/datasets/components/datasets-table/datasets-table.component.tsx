import {
    ArrowRightOutlined,
    BarChartOutlined,
    CalendarOutlined,
    DatabaseOutlined,
    ShoppingCartOutlined,
    StarFilled,
    TeamOutlined,
} from '@ant-design/icons';
import { Button, Card, Flex, Form, Input, Pagination, Space, Tag, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset';
import { createDatasetIdPath } from '@/types/navigation.ts';

function filterDatasets(datasets: DatasetsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return datasets;
    }
    return datasets.filter((dataset) => dataset.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

function filterDatasetsByRoles(datasets: DatasetsGetContract, selectedDatasetIds: string[]) {
    if (!selectedDatasetIds.length) {
        return datasets;
    }

    return datasets.filter((dataset) => {
        return selectedDatasetIds.includes(dataset.id);
    });
}

export function DatasetsTable() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedDatasetIds, setSelectedDatasetIds] = useState<string[]>([]);

    const { data: datasets = [] } = useGetAllDatasetsQuery();

    const [searchTerm, setSearchTerm] = useState('');

    const filteredDatasets = useMemo(() => {
        let filtered = filterDatasets(datasets, searchTerm);
        filtered = filterDatasetsByRoles(filtered, selectedDatasetIds);
        return filtered;
    }, [datasets, searchTerm, selectedDatasetIds]);

    const { pagination, handlePaginationChange } = useTablePagination(filteredDatasets);
    const handleSearchChange = (value: string) => {
        setSearchTerm(value);
    };

    const CAPTURE_SEARCH_EVENT_DELAY = 750;

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

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            ...pagination,
            current: page,
            pageSize,
        });
    };

    function navigateToDataset(datasetId: string) {
        navigate(createDatasetIdPath(datasetId));
    }
    const handleAddToBasket = (id: string) => {
        console.log('Add to basket clicked for dataset with id:', id);
    };

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
                    display: 'flex',
                    flexWrap: 'wrap',
                }}
            >
                {filteredDatasets.map((dataset) => (
                    <Card
                        key={dataset.id}
                        styles={{ body: { padding: 12 } }}
                        style={{
                            flex: '1 1 360',
                            margin: 8,
                            minWidth: 360,
                            maxWidth: 360,
                            boxShadow: '0 2px 8px #f0f1f2',
                        }}
                    >
                        <Space direction="vertical" style={{ width: '100%' }} size="middle">
                            <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                                <div>
                                    <Typography.Title level={5} style={{ marginBottom: 0 }}>
                                        {dataset.name}
                                    </Typography.Title>
                                    <Typography.Text>
                                        {dataset.description || 'No description available.'}
                                    </Typography.Text>
                                    <div style={{ marginTop: 12 }}>
                                        <Tag>Transactions</Tag>
                                        <Tag>Payments</Tag>
                                        <Tag>Customer Data</Tag>
                                        <Tag>+1</Tag>
                                    </div>
                                </div>
                            </Space>

                            <div
                                style={{
                                    display: 'grid',
                                    gridTemplateColumns: '1fr 1fr',
                                    gap: 8,
                                    marginTop: 4,
                                }}
                            >
                                <div>
                                    <DatabaseOutlined /> <Typography.Text type="secondary">Data Type</Typography.Text>
                                    <br />
                                    <Typography.Text strong>Transactional</Typography.Text>
                                </div>
                                <div>
                                    <CalendarOutlined />{' '}
                                    <Typography.Text type="secondary">Last Updated</Typography.Text>
                                    <br />
                                    <Typography.Text strong>2 hours ago</Typography.Text>
                                </div>
                                <div>
                                    <TeamOutlined /> <Typography.Text type="secondary">Owner</Typography.Text>
                                    <br />
                                    <Typography.Text strong>Finance Team</Typography.Text>
                                </div>
                                <div>
                                    <DatabaseOutlined />{' '}
                                    <Typography.Text type="secondary">Managed Assets</Typography.Text>
                                    <br />
                                    <Typography.Text strong>18</Typography.Text>
                                </div>
                                <div>
                                    <BarChartOutlined /> <Typography.Text type="secondary">Domain</Typography.Text>
                                    <br />
                                    <Typography.Text strong>Sales & Revenue</Typography.Text>
                                </div>
                                <div>
                                    <BarChartOutlined /> <Typography.Text type="secondary">Usage</Typography.Text>
                                    <br />
                                    <Typography.Text strong>1247 monthly queries</Typography.Text>
                                </div>
                            </div>

                            <div style={{ borderTop: '2px solid #f0f0f0' }} />

                            <Space style={{ float: 'right' }}>
                                <Button icon={<ShoppingCartOutlined />} onClick={() => handleAddToBasket(dataset.id)}>
                                    Add to Cart
                                </Button>
                                <Button type="primary" onClick={() => navigateToDataset(dataset.id)}>
                                    View Details
                                </Button>
                            </Space>
                        </Space>
                    </Card>
                ))}
            </Flex>

            <Pagination
                current={0}
                pageSize={10}
                total={filteredDatasets.length}
                onChange={handlePageChange}
                size="small"
            />
        </div>
    );
}
