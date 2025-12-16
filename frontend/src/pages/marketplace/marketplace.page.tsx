import { usePostHog } from '@posthog/react';
import { Flex, Pagination } from 'antd';
import { DeepChat } from 'deep-chat-react';
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
        >
            <DeepChat
                connect={{
                    url: 'http://localhost:5050/api/chat',
                    method: 'POST',
                }}
                requestInterceptor={(details) => {
                    // Optional: You can inspect details.body here to see it sends the full array
                    console.log('Sending history:', details.body.messages);
                    return details;
                }}
                responseInterceptor={(response) => {
                    let finalText = response.response;

                    // If there were thoughts/steps, prepend them nicely
                    if (response.thoughts && response.thoughts.length > 0) {
                        const steps = response.thoughts.map((x: string) => `Requesting tool: ${x}`).join('\n');

                        // Add a "Thought block" above the answer
                        finalText = `*${steps}*\n\n---\n\n${finalText}`;
                    }

                    // Handle Sources (Side Panel)
                    // if (response.tool_data) setSources(response.tool_data);

                    return { text: finalText };
                }}
                // 4. visual customization
                style={{
                    borderRadius: '10px',
                    width: '100%',
                    height: '500px',
                    border: '1px solid #ccc',
                }}
                introMessage={{ text: 'Hello! Ask me anything.' }}
                textInput={{ placeholder: { text: 'Type your query here...' } }}
            />
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
        </SearchPage>
    );
}
