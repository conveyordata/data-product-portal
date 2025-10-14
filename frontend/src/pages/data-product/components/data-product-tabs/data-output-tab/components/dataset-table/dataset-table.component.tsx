import { Button, Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useRemoveDataOutputMutation,
    useRemoveDatasetFromDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetByIdQuery, useRemoveDatasetMutation } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DatasetContract } from '@/types/dataset/dataset.contract.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './dataset-table.module.scss';
import { getDataProductDatasetsColumns } from './dataset-table-columns.tsx';

type Props = {
    dataProductId: string;
    datasets: DatasetsGetContract;
};
export function DatasetTable({ dataProductId, datasets }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    // Get all unique dataset IDs
    const datasetIds = useMemo(() => datasets.map((dataset) => dataset.id), [datasets]);

    // Fetch enriched data for all datasets unconditionally
    const enrichedDatasetQueries = datasetIds.map((datasetId) => useGetDatasetByIdQuery(datasetId));

    // Fetch delete permissions for all datasets unconditionally
    const deletePermissionQueries = datasetIds.map((datasetId) =>
        useCheckAccessQuery({
            resource: datasetId,
            action: AuthorizationAction.DATASET__DELETE,
        }),
    );

    const enrichedDatasets = useMemo(() => {
        return enrichedDatasetQueries
            .map((query) => query.data)
            .filter((dataset): dataset is DatasetContract => dataset !== undefined);
    }, [enrichedDatasetQueries]);

    const isLoadingDatasets = enrichedDatasetQueries.some((query) => query.isLoading);

    const [removeDataset] = useRemoveDatasetMutation();
    const [unlinkDataset] = useRemoveDatasetFromDataOutputMutation();

    const { pagination, handlePaginationChange } = useTablePagination(datasets, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DatasetContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveDataset = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDataset(datasetId).unwrap();
                dispatchMessage({
                    content: t('Dataset {{name}} has been successfully removed', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove dataset', error);
            }
        },
        [removeDataset, t],
    );

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

    const handleRemoveDataOutputLink = useCallback(
        async (datasetId: string, dataOutputId: string) => {
            try {
                await unlinkDataset({ dataOutputId, datasetId }).unwrap();
                dispatchMessage({
                    content: t('Data output unlinked successfully'),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to unlink data output', error);
                dispatchMessage({
                    content: t('Failed to unlink data output'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, t],
    );

    const getCanRemove = useCallback(
        (datasetId: string) => {
            const datasetIndex = datasetIds.indexOf(datasetId);
            if (datasetIndex === -1) return false;
            return deletePermissionQueries[datasetIndex]?.data?.allowed ?? false;
        },
        [deletePermissionQueries, datasetIds],
    );

    const columns: TableColumnsType<DatasetContract> = useMemo(() => {
        return getDataProductDatasetsColumns({
            t,
            onRemoveDataset: handleRemoveDataset,
            getCanRemove,
            onRemoveDataOutputLink: handleRemoveDataOutputLink,
        });
    }, [t, handleRemoveDataset, getCanRemove, handleRemoveDataOutputLink]);

    if (!dataProduct) return null;

    const canCreateDataset = (access?.allowed && access2?.allowed) || false;

    return (
        <Flex className={styles.dataOutputListContainer}>
            <Table<DatasetContract>
                loading={isLoadingDataProduct || isLoadingDatasets}
                className={styles.dataOutputListTable}
                columns={columns}
                dataSource={enrichedDatasets}
                title={() => (
                    <Link to={`${ApplicationPaths.DatasetNew}?dataProductId=${dataProductId}`}>
                        <Button
                            disabled={!canCreateDataset}
                            type={'primary'}
                            className={styles.formButton}
                            // onClick={handleOpen}
                        >
                            {t('Add Dataset')}
                        </Button>
                    </Link>
                )}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} datasets', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    hideOnSinglePage: false,
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
