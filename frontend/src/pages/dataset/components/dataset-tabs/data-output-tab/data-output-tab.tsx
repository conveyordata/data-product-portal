import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { DataOutputTable } from '@/pages/dataset/components/dataset-tabs/data-output-tab/components/data-output-table/data-output-table.component';
import {
    type TechnicalAssetLink,
    useGetOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import type { SearchForm } from '@/types/shared';
import styles from './data-output-tab.module.scss';

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
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(dataset?.technical_asset_links || [], searchTerm);
    }, [dataset?.technical_asset_links, searchTerm]);

    return (
        <Flex vertical className={`${styles.container} ${filteredDataOutputs.length === 0 && styles.paginationGap}`}>
            <Searchbar
                placeholder={t('Search Technical Assets by name')}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                form={searchForm}
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
