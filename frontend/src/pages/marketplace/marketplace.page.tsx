import { usePostHog } from '@posthog/react';
import { Flex, Pagination } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import SearchPage from '@/components/search-page/search-page.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset';
import { DatasetMarketplaceCard } from './dataset-marketplace-card/dataset-marketplace-card.component';

function filterDatasets(datasets: DatasetsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return datasets;
    }
    return datasets.filter((dataset) => dataset.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export function Marketplace() {
    const { t } = useTranslation();
    const posthog = usePostHog();

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

        // clear if searchTerm gets updated beforehand
        return () => clearTimeout(timeoutId);
    }, [posthog, searchTerm]);

    return (
        <SearchPage
            title={t('Marketplace')}
            searchPlaceholder={t('Search output ports by name')}
            onSearch={handleSearchChange}
        >
            <Flex wrap="wrap" gap={'small'}>
                {paginatedOutputPorts.map((dataset) => (
                    <DatasetMarketplaceCard key={dataset.id} dataset={dataset} />
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
        </SearchPage>
    );
}
