import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductTable } from '@/pages/dataset/components/dataset-tabs/data-product-tab/components/data-product-table/data-product-table.component';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import type { DataProductLink } from '@/types/dataset';

type Props = {
    datasetId: string;
};

function filterDataProducts(dataProductLinks: DataProductLink[], searchTerm: string) {
    return (
        dataProductLinks.filter(
            (item) =>
                item?.data_product?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                item?.data_product?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DataProductTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const [searchTerm, setSearchTerm] = useState<string>('');
    const datasetDataProducts = useMemo(() => {
        return dataset?.data_product_links || [];
    }, [dataset?.data_product_links]);

    const filteredDataProducts = useMemo(() => {
        return filterDataProducts(datasetDataProducts, searchTerm);
    }, [datasetDataProducts, searchTerm]);

    return (
        <Flex vertical gap="middle">
            <Input.Search
                placeholder={t('Search Data Products by name')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <DataProductTable datasetId={datasetId} dataProducts={filteredDataProducts} isLoading={isLoading} />
        </Flex>
    );
}
