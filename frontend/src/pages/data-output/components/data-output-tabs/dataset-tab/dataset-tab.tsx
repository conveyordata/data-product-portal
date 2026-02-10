import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import {
    type OutputPortLink,
    useGetTechnicalAssetQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import type { SearchForm } from '@/types/shared';
import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';
import styles from './dataset-tab.module.scss';

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

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredDatasets = useMemo(() => {
        return filterDatasets(technicalAsset?.output_port_links ?? [], searchTerm);
    }, [technicalAsset?.output_port_links, searchTerm]);

    return (
        <Flex vertical className={`${styles.container} ${filteredDatasets.length === 0 && styles.paginationGap}`}>
            <Searchbar
                placeholder={t('Search Output Ports by name')}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                form={searchForm}
            />

            <DatasetTable dataProductId={dataProductId} dataOutputId={technicalAssetId} datasets={filteredDatasets} />
        </Flex>
    );
}
