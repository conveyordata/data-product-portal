import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
    type OutputPortLink,
    useGetTechnicalAssetQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';

function filterDatasets(outputPortLinks: OutputPortLink[], searchTerm: string) {
    return (
        outputPortLinks.filter(
            (outputPortLink) =>
                outputPortLink?.output?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                outputPortLink?.output?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    technicalAssetId: string;
    dataProductId: string;
};
export function DatasetTab({ technicalAssetId, dataProductId }: Props) {
    const { t } = useTranslation();

    const { data: technicalAsset } = useGetTechnicalAssetQuery({ id: technicalAssetId, dataProductId });
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredDatasets = useMemo(() => {
        return filterDatasets(technicalAsset?.output_port_links ?? [], searchTerm);
    }, [technicalAsset?.output_port_links, searchTerm]);

    return (
        <Flex vertical gap="middle">
            <Input.Search
                placeholder={t('Search Output Ports by name')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <DatasetTable dataProductId={dataProductId} dataOutputId={technicalAssetId} datasets={filteredDatasets} />
        </Flex>
    );
}
