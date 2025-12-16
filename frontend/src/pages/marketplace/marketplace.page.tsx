import { StarFilled } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Button, Flex, Pagination, Space, Typography } from 'antd';
import { use, useEffect, useMemo, useState } from 'react';
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
    const [reasoningStream, setReasoning] = useState<string>('');
    const [toggle, setToggle] = useState<boolean>(false);

    useEffect(() => {
        if (debouncedSearchTerm?.length < 3) return;

        const fetchStream = async () => {
            setDatasets([]);
            const res = await fetch(`http://localhost:5050/api/datasets/search_ai_stream?query=${debouncedSearchTerm}`);
            const reader = res.body!.getReader();
            const decoder = new TextDecoder();

            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // assuming your backend streams JSONL (one JSON per line)
                const lines = buffer.split('\n');
                buffer = lines.pop()!; // keep the last partial line for next iteration

                for (const line of lines) {
                    if (!line.trim()) continue;
                    const obj = JSON.parse(line);
                    const dataset = JSON.parse(obj.payload);
                    console.log('dataset:', dataset);
                    setDatasets((prev) => [...prev, dataset]);
                    // setReasoning(prev => prev + obj.reasoning); // append reasoning
                }
            }

            if (buffer.trim()) {
                const obj = JSON.parse(buffer);
                setDatasets((prev) => [...prev, ...obj.datasets]);
                setReasoning((prev) => prev + obj.reasoning);
            }
        };

        fetchStream();
    }, [debouncedSearchTerm]);

    const {
        data: { datasets: datasetSearchResult, reasoning } = { datasets: [], reasoning: '' },
        isFetching: datasetSearchFetching,
    } = useSearchDatasetsQuery(
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
                <Button
                    icon={<StarFilled />}
                    onClick={() => setToggle(!toggle)}
                    style={{
                        background: 'linear-gradient(90deg, #7A5AF8 0%, #D6429A 100%)',
                        borderColor: 'transparent',
                        color: '#fff',
                        fontWeight: 500,
                    }}
                >
                    Deep search
                </Button>
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
