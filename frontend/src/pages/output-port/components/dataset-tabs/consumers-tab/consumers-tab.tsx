import { Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type OutputPortInputPort,
    useGetInputPortsForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { ConsumersTable } from './components/consumers-table/consumers-table.component';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

function filterDataProducts(dataProductLinks: OutputPortInputPort[], searchTerm: string) {
    return (
        dataProductLinks.filter((item) =>
            item?.consuming_abstract_data_product.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function ConsumersTab({ outputPortId, dataProductId }: Props) {
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
            <ConsumersTable
                outputPortId={outputPortId}
                dataProductId={dataProductId}
                dataProducts={filteredDataProducts}
                isLoading={isLoading}
            />
        </Flex>
    );
}
