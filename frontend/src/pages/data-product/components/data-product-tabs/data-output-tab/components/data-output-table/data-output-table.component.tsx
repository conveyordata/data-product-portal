import { Button, Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useModal } from '@/hooks/use-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useRemoveDataOutputDatasetLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputsGetContract } from '@/types/data-output';
import { AddDataOutputPopup } from '../add-data-output-popup/add-data-output-popup.tsx';
import styles from './data-output-table.module.scss';
import { getDataProductDataOutputsColumns } from './data-output-table-columns.tsx';

type Props = {
    dataProductId: string;
    dataOutputs: DataOutputsGetContract;
};
export function DataOutputTable({ dataProductId, dataOutputs }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [removeDataOutput] = useRemoveDataOutputMutation();
    const [unlinkDataset] = useRemoveDataOutputDatasetLinkMutation();

    const { pagination, handlePaginationChange } = useTablePagination(dataOutputs, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataOutputsGetContract[0]>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_DATA_OUTPUT,
        },
        { skip: !dataProductId },
    );

    const handleRemoveDataOutput = useCallback(
        async (dataOutputId: string, name: string) => {
            try {
                await removeDataOutput(dataOutputId).unwrap();
                dispatchMessage({
                    content: t('Data Output {{name}} has been successfully removed', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove data output', error);
            }
        },
        [removeDataOutput, t],
    );

    const handleRemoveDatasetLink = useCallback(
        async (dataOutputId: string, datasetId: string, datasetLinkId: string) => {
            try {
                await unlinkDataset({ dataOutputId, datasetId, datasetLinkId }).unwrap();
                dispatchMessage({
                    content: t('Dataset unlinked successfully'),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to unlink dataset', error);
                dispatchMessage({
                    content: t('Failed to unlink dataset'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, t],
    );

    const { data: deleteDataOutput } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__DELETE_DATA_OUTPUT,
        },
        { skip: !dataProductId },
    );

    const columns: TableColumnsType<DataOutputsGetContract[0]> = useMemo(() => {
        return getDataProductDataOutputsColumns({
            t,
            canRemove: deleteDataOutput?.allowed ?? false,
            onRemoveDataOutput: handleRemoveDataOutput,
            onRemoveDatasetLink: handleRemoveDatasetLink,
        });
    }, [t, deleteDataOutput, handleRemoveDataOutput, handleRemoveDatasetLink]);

    if (!dataProduct) return null;
    const { isVisible, handleOpen, handleClose } = useModal();

    const canCreateDataOutput = access?.allowed || false;

    return (
        <Flex vertical className={styles.dataOutputListContainer}>
            <Table<DataOutputsGetContract[0]>
                loading={isLoadingDataProduct}
                className={styles.dataOutputListTable}
                title={() => (
                    <Button
                        disabled={!canCreateDataOutput}
                        type={'primary'}
                        className={styles.formButton}
                        onClick={handleOpen}
                    >
                        {t('Add Data Output')}
                    </Button>
                )}
                columns={columns}
                dataSource={dataOutputs}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} data outputs', {
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
            {isVisible && <AddDataOutputPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
