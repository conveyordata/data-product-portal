import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import type { DataOutputDatasetLink } from '@/types/data-output';

import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';

function filterDatasets(datasetLinks: DataOutputDatasetLink[], searchTerm: string) {
    return (
        datasetLinks.filter(
            (datasetLink) =>
                datasetLink?.dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                datasetLink?.dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    dataOutputId: string;
};
export function DatasetTab({ dataOutputId }: Props) {
    const { t } = useTranslation();

    const { data: dataOutput, isFetching: isFetchingInitialValues } = useGetDataOutputByIdQuery(dataOutputId || '', {
        skip: !dataOutputId,
    });
    const { data: dataProduct } = useGetDataProductByIdQuery(dataOutput?.owner.id ?? '', {
        skip: !dataOutput?.owner.id || isFetchingInitialValues || !dataOutputId,
    });
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataOutput?.dataset_links ?? [], searchTerm);
    }, [dataOutput?.dataset_links, searchTerm]);

    return (
        <Flex vertical gap="middle">
            <Input.Search
                placeholder={t('Search Output Ports by name')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <DatasetTable dataProductId={dataProduct?.id} dataOutputId={dataOutputId} datasets={filteredDatasets} />
        </Flex>
    );
}
