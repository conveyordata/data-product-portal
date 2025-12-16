import { usePostHog } from '@posthog/react';
import { Flex, Pagination, Switch, Typography } from 'antd';
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

    const [datasetSearchResultStream, setDatasets] = useState<any[]>([]);
    const [toggle, setToggle] = useState<boolean>(false);

    useEffect(() => {
        if (debouncedSearchTerm?.length < 3) return;

        const controller = new AbortController();
        const { signal } = controller;

        let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

        const fetchStream = async () => {
            try {
                setDatasets([]);

                const res = await fetch(
                    `http://localhost:5050/api/datasets/search_ai_stream?query=${encodeURIComponent(debouncedSearchTerm)}`,
                    { signal },
                );

                if (!res.body) return;

                reader = res.body.getReader();
                const decoder = new TextDecoder();

                let buffer = '';

                while (!signal.aborted) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });

                    const lines = buffer.split('\n');
                    buffer = lines.pop() ?? '';

                    for (const line of lines) {
                        if (!line.trim()) continue;
                        const obj = JSON.parse(line);
                        const dataset = JSON.parse(obj.payload);
                        setDatasets((prev) => [...prev, dataset]);
                    }
                }
            } catch (err: unknown) {
                // Abort is expected when a new query starts
                if (err instanceof DOMException && err.name === 'AbortError') return;
                throw err;
            }
        };

        void fetchStream();

        return () => {
            controller.abort();
            reader?.cancel().catch(() => {
                // ignore: reader may already be closed
            });
        };
    }, [debouncedSearchTerm]);

    const { data: { datasets: datasetSearchResult, reasoning } = { datasets: [], reasoning: '' } } =
        useSearchDatasetsQuery(
            {
                query: debouncedSearchTerm,
            },
            { skip: debouncedSearchTerm?.length < 3 },
        );

    const finalDatasetResults = useMemo(() => {
        if (toggle) {
            return debouncedSearchTerm?.length >= 3 ? datasetSearchResultStream : datasets;
        }
        return debouncedSearchTerm?.length >= 3 ? datasetSearchResult : datasets;
    }, [toggle, datasetSearchResult, datasetSearchResultStream, debouncedSearchTerm, datasets]);

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
            actions={
                <Switch
                    checkedChildren="Deep search"
                    unCheckedChildren="Semantic search"
                    defaultChecked={false}
                    onChange={(checked: boolean) => setToggle(checked)}
                />
            }
            // datasetSearchFetching={datasetSearchFetching}
        >
            {reasoning && <Typography.Paragraph>{reasoning}</Typography.Paragraph>}
            <Flex wrap="wrap" gap={'small'}>
                {paginatedOutputPorts.map((dataset) => (
                    <DatasetMarketplaceCard key={dataset.id} dataset={dataset} query={searchTerm} />
                ))}
            </Flex>
            {finalDatasetResults && finalDatasetResults.length > pageSize && (
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
