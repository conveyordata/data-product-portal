import {
    BarChartOutlined,
    DatabaseOutlined,
    EyeOutlined,
    NumberOutlined,
    ShareAltOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import {
    Button,
    Card,
    Descriptions,
    type DescriptionsProps,
    Flex,
    Form,
    Input,
    Pagination,
    Space,
    Tag,
    Typography,
} from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset';
import { createDatasetIdPath } from '@/types/navigation.ts';
import styles from './marketplace.module.scss';

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

    const filteredOutputPorts = useMemo(() => {
        return filterDatasets(datasets, searchTerm);
    }, [datasets, searchTerm]);

    const paginatedOutputPorts = useMemo(() => {
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        return filteredOutputPorts.slice(startIndex, endIndex);
    }, [filteredOutputPorts, currentPage]);

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
                        {dataset.data_product_name}
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
                children: t('{{count}} data products', { count: dataset.data_product_count }),
            },
        ];
        return items;
    }

    return (
        <div>
            <Flex align={'center'} gap={'small'}>
                <Typography.Title level={3}>{t('Marketplace')}</Typography.Title>
                <Form style={{ flex: 1 }}>
                    <Input.Search
                        style={{ height: '40px' }}
                        placeholder={t('Search output ports by name')}
                        value={searchTerm}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        allowClear
                    />
                </Form>
            </Flex>
            <Flex wrap="wrap" className={styles.marketplacePageContainer}>
                {paginatedOutputPorts.map((dataset) => (
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
                ))}
            </Flex>
            {filteredOutputPorts.length > pageSize && (
                <Flex
                    key="pagination-container"
                    justify={'flex-end'}
                    style={{
                        marginTop: 12,
                    }}
                >
                    <Pagination
                        current={currentPage}
                        pageSize={pageSize}
                        total={filteredOutputPorts.length}
                        onChange={handlePageChange}
                        showSizeChanger={false} // Disable page size changer
                    />
                </Flex>
            )}
        </div>
    );
}
