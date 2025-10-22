import { Button, Flex, Form, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { DatasetCard } from '@/components/datasets/dataset-card/dataset-card.component';
import { Searchbar } from '@/components/form';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import type { SearchForm } from '@/types/shared';
import styles from './dataset-table.module.scss';

type Props = {
    dataProductId: string;
    datasets: DatasetsGetContract;
    isDragActive?: boolean;
    draggedDataOutputId?: string | null;
};

export function DatasetTable({ dataProductId, datasets, isDragActive, draggedDataOutputId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    const { data: access_create_dataset } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.GLOBAL__CREATE_DATASET,
        },
        { skip: !dataProductId },
    );
    const { data: can_link_data_output } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
        },
        { skip: !dataProductId },
    );
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredDatasets = useMemo(() => {
        if (!searchTerm) return datasets;
        return datasets.filter(
            (dataset) =>
                dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        );
    }, [datasets, searchTerm]);

    if (!dataProduct) return null;

    // TODO To be seen if these are the right ACCESS checks we want here or if we need to create new ones.
    const canCreateDataset = (access_create_dataset?.allowed && can_link_data_output?.allowed) || false;

    return (
        <Flex vertical className={`${styles.container} ${isDragActive ? styles.dragActive : ''}`}>
            <Flex justify="space-between" align="center" className={styles.header}>
                <Typography.Title level={4}>{t('Output Ports')}</Typography.Title>
                <Link to={`${ApplicationPaths.DatasetNew}?dataProductId=${dataProductId}`}>
                    <Button disabled={!canCreateDataset} type="primary" loading={isLoadingDataProduct}>
                        {t('Add Output Port')}
                    </Button>
                </Link>
            </Flex>

            <Searchbar
                placeholder={t('Search output ports by name or description')}
                formItemProps={{ initialValue: '', className: styles.searchBar }}
                form={searchForm}
            />

            <Flex vertical className={styles.cardsGrid}>
                {filteredDatasets.map((dataset) => (
                    <DatasetCard
                        key={dataset.id}
                        datasetId={dataset.id}
                        isDragActive={isDragActive}
                        draggedDataOutputId={draggedDataOutputId}
                    />
                ))}

                {filteredDatasets.length === 0 && (
                    <Flex className={styles.emptyState}>
                        <Typography.Text type="secondary">
                            {searchTerm ? t('No datasets found matching your search') : t('No datasets found')}
                        </Typography.Text>
                    </Flex>
                )}
            </Flex>
        </Flex>
    );
}
