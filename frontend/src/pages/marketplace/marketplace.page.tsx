import { Flex, Form, Input, Pagination, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDebounce } from 'use-debounce';
import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useGetAllDatasetsQuery, useSearchDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { DatasetMarketplaceCard } from './dataset-marketplace-card/dataset-marketplace-card.component';
import styles from './marketplace.module.scss';

export function Marketplace() {
    const { t } = useTranslation();

    const pageSize = 12;
    const [currentPage, setCurrentPage] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearchTerm] = useDebounce(searchTerm, 500);
    const { data: datasets = [] } = useGetAllDatasetsQuery();

    const { data: datasetSearchResult = [] } = useSearchDatasetsQuery(
        {
            query: debouncedSearchTerm,
        },
        { skip: debouncedSearchTerm?.length < 3 },
    );

    const finalDatasetResults = debouncedSearchTerm?.length >= 3 ? datasetSearchResult : datasets;

    const paginatedOutputPorts = useMemo(() => {
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        return finalDatasetResults.slice(startIndex, endIndex);
    }, [finalDatasetResults, currentPage]);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    const handleSearchChange = (value: string) => {
        setSearchTerm(value);
        setCurrentPage(1); // Reset to first page on search
    };

    useEffect(() => {
        if (debouncedSearchTerm?.length < 3) return;

        posthog.capture(PosthogEvents.MARKETPLACE_SEARCHED_DATASET, {
            search_term: debouncedSearchTerm,
        });
    }, [debouncedSearchTerm]);

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
                    <DatasetMarketplaceCard key={dataset.id} dataset={dataset} />
                ))}
            </Flex>
            {finalDatasetResults.length > pageSize && (
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
                        total={finalDatasetResults.length}
                        onChange={handlePageChange}
                        showSizeChanger={false} // Disable page size changer
                    />
                </Flex>
            )}
        </div>
    );
}
