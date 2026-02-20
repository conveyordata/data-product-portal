import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputTable } from '@/pages/dataset/components/dataset-tabs/data-output-tab/components/data-output-table/data-output-table.component';
import {
    type TechnicalAssetLink,
    useGetOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

function filterDataOutputs(dataOutputLinks: TechnicalAssetLink[], searchTerm: string) {
    return (
        dataOutputLinks.filter(
            (item) =>
                item?.technical_asset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                item?.technical_asset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    datasetId: string;
    dataProductId: string;
};
export function DataOutputTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isLoading } = useGetOutputPortQuery({ id: datasetId, dataProductId });
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(dataset?.technical_asset_links || [], searchTerm);
    }, [dataset?.technical_asset_links, searchTerm]);

    return (
        <Flex vertical gap={'middle'}>
            <Input.Search
                placeholder={t('Search Technical Assets by name')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <DataOutputTable
                dataOutputs={filteredDataOutputs}
                isLoading={isLoading}
                datasetId={datasetId}
                dataProductId={dataProductId}
            />
        </Flex>
    );
}
