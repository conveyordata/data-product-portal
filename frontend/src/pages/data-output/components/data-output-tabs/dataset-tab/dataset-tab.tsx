import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import type { DataOutputDatasetLink } from '@/types/data-output';
import type { SearchForm } from '@/types/shared';

import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';
import styles from './dataset-tab.module.scss';

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

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataOutput?.dataset_links ?? [], searchTerm);
    }, [dataOutput?.dataset_links, searchTerm]);

    return (
        <Flex vertical className={`${styles.container} ${filteredDatasets.length === 0 && styles.paginationGap}`}>
            <Searchbar
                placeholder={t('Search Output Ports by name')}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                form={searchForm}
            />

            <DatasetTable dataProductId={dataProduct?.id} dataOutputId={dataOutputId} datasets={filteredDatasets} />
        </Flex>
    );
}
