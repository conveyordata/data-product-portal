import { usePostHog } from '@posthog/react';
import { Alert, Button, Flex, Pagination, Popover, Space, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDebounce } from 'use-debounce';
import SearchPage from '@/components/search-page/search-page.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useGetAllDatasetsQuery, useSearchDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { DatasetMarketplaceCard } from './dataset-marketplace-card/dataset-marketplace-card.component';

export function Marketplace() {
    const { t } = useTranslation();
    const posthog = usePostHog();

    const pageSize = 12;
    const [currentPage, setCurrentPage] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearchTerm] = useDebounce(searchTerm, 500);
    const { data: datasets = [] } = useGetAllDatasetsQuery();

    const { data: datasetSearchResult = [], isFetching: datasetSearchFetching } = useSearchDatasetsQuery(
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
    }, [posthog, debouncedSearchTerm]);

    return (
        <SearchPage
            title={t('Marketplace')}
            searchPlaceholder={t('Ask a business question to find the relevant data')}
            onSearch={handleSearchChange}
            datasetSearchFetching={datasetSearchFetching}
            actions={
                <Popover title={'Try this alternative query'} content={'How is our ROI'}>
                    <Button type={'primary'} disabled={debouncedSearchTerm === ''}>
                        Can't find what you're looking for?
                    </Button>
                </Popover>
            }
        >
            <Flex gap={'small'} vertical>
                {/*<Alert*/}
                {/*    closable*/}
                {/*    description={t("If you found what your were looking for add it to your cart!")}*/}
                {/*    type="info"*/}
                {/*/>*/}
                <Flex wrap="wrap" gap={'small'}>
                    {paginatedOutputPorts.map((dataset) => (
                        <DatasetMarketplaceCard key={dataset.id} dataset={dataset} query={searchTerm} />
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
                            showTotal={(total, range) =>
                                t('Showing {{range0}}-{{range1}} of {{total}} output ports', {
                                    range0: range[0],
                                    range1: range[1],
                                    total: total,
                                })
                            }
                        />
                    </Flex>
                )}
            </Flex>
        </SearchPage>
    );
}
