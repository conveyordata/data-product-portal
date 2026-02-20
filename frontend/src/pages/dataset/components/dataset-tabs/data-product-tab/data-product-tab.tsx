import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductTable } from '@/pages/dataset/components/dataset-tabs/data-product-tab/components/data-product-table/data-product-table.component';
import {
    type InputPort,
    useGetInputPortsForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

function filterDataProducts(dataProductLinks: InputPort[], searchTerm: string) {
    return (
        dataProductLinks.filter((item) =>
            item?.data_product.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DataProductTab({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: { input_ports: inputPorts = [] } = {}, isLoading } = useGetInputPortsForOutputPortQuery({
        outputPortId: outputPortId,
        dataProductId,
    });
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredDataProducts = useMemo(() => {
        return filterDataProducts(inputPorts, searchTerm);
    }, [inputPorts, searchTerm]);

    return (
        <Flex vertical gap="middle">
            <Input.Search
                placeholder={t('Search Data Products by name')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <DataProductTable datasetId={outputPortId} dataProducts={filteredDataProducts} isLoading={isLoading} />
        </Flex>
    );
}
