import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { DataProductTable } from '@/pages/dataset/components/dataset-tabs/data-product-tab/components/data-product-table/data-product-table.component';
import {
    type InputPort,
    useGetInputPortsForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import type { SearchForm } from '@/types/shared';
import styles from './data-product-tab.module.scss';

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
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataProducts = useMemo(() => {
        return filterDataProducts(inputPorts, searchTerm);
    }, [inputPorts, searchTerm]);

    return (
        <Flex vertical className={`${styles.container} ${filteredDataProducts.length === 0 && styles.paginationGap}`}>
            <Searchbar
                placeholder={t('Search Data Products by name')}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                form={searchForm}
            />
            <DataProductTable datasetId={outputPortId} dataProducts={filteredDataProducts} isLoading={isLoading} />
        </Flex>
    );
}
