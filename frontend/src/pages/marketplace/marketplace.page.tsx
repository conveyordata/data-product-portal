import { Flex, Form, Input, Pagination, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import posthog from '@/config/posthog-config.ts';
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

    return (
        <div>
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
                    />
                </Flex>
            )}
        </div>
    );
}
