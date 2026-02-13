import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputTable } from '@/pages/dataset/components/dataset-tabs/data-output-tab/components/data-output-table/data-output-table.component';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import type { DataOutputLink } from '@/types/dataset';

function filterDataOutputs(dataOutputLinks: DataOutputLink[], searchTerm: string) {
    return (
        dataOutputLinks.filter(
            (item) =>
                item?.data_output?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                item?.data_output?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    datasetId: string;
};
export function DataOutputTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const [searchTerm, setSearchTerm] = useState<string>('');
    const datasetDataOutputs = useMemo(() => {
        return dataset?.data_output_links || [];
    }, [dataset?.data_output_links]);

    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(datasetDataOutputs, searchTerm);
    }, [datasetDataOutputs, searchTerm]);

    return (
        <Flex vertical gap={'middle'}>
            <Input.Search
                placeholder={t('Search Technical Assets by name')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <DataOutputTable dataOutputs={filteredDataOutputs} isLoading={isLoading} datasetId={datasetId} />
        </Flex>
    );
}
