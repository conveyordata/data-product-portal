import { Button, Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { DatasetCard } from '@/components/datasets/dataset-card/dataset-card.component';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
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

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.GLOBAL__CREATE_DATASET,
        },
        { skip: !dataProductId },
    );
    const { data: access2 } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
        },
        { skip: !dataProductId },
    );

    if (!dataProduct) return null;

    const canCreateDataset = (access?.allowed && access2?.allowed) || false;

    return (
        <Flex vertical className={`${styles.container} ${isDragActive ? styles.dragActive : ''}`}>
            <Flex justify="space-between" align="center" className={styles.header}>
                <Typography.Title level={4}>{t('Datasets')}</Typography.Title>
                <Link to={`${ApplicationPaths.DatasetNew}?dataProductId=${dataProductId}`}>
                    <Button disabled={!canCreateDataset} type="primary" loading={isLoadingDataProduct}>
                        {t('Add Dataset')}
                    </Button>
                </Link>
            </Flex>

            <div className={styles.cardsGrid}>
                {datasets.map((dataset) => (
                    <DatasetCard
                        key={dataset.id}
                        datasetId={dataset.id}
                        isDragActive={isDragActive}
                        draggedDataOutputId={draggedDataOutputId}
                    />
                ))}

                {datasets.length === 0 && (
                    <div className={styles.emptyState}>
                        <Typography.Text type="secondary">{t('No datasets found')}</Typography.Text>
                    </div>
                )}
            </div>
        </Flex>
    );
}
