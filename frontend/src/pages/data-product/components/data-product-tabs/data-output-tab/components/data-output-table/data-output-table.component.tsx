import { Flex, Table, type TableColumnsType, TableProps } from 'antd';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useModal } from '@/hooks/use-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    useRemoveDataOutputMutation,
    useRemoveDatasetFromDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataOutputsGetContract } from '@/types/data-output';

import { AddDatasetPopup } from '../add-dataset-popup/add-dataset-popup.tsx';
import styles from './data-output-table.module.scss';
import { getDataProductDataOutputsColumns } from './data-output-table-columns.tsx';

type Props = {
    isCurrentUserDataProductOwner: boolean;
    dataProductId: string;
    dataOutputs: DataOutputsGetContract;
};

export function DataOutputTable({ isCurrentUserDataProductOwner, dataProductId, dataOutputs }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    const [removeDatasetFromDataOutput] = useRemoveDatasetFromDataOutputMutation();
    const [removeDataOutput] = useRemoveDataOutputMutation();

    const [dataOutput, setDataOutput] = useState<string | undefined>(undefined);
    const { isVisible, handleOpen, handleClose } = useModal();
    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataOutputsGetContract[0]>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    useEffect(() => {
        resetPagination();
    }, [dataOutputs, resetPagination]);

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

    const handleRemoveDatasetFromDataOutput = useCallback(
        async (datasetId: string, dataOutputId: string, name: string) => {
            try {
                await removeDatasetFromDataOutput({ datasetId, dataOutputId: dataOutputId }).unwrap();
                dispatchMessage({
                    content: t('Dataset {{name}} has been removed from data output', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove dataset from data output', error);
            }
        },
        [removeDatasetFromDataOutput, t],
    );

    const columns: TableColumnsType<DataOutputsGetContract[0]> = useMemo(() => {
        return getDataProductDataOutputsColumns({
            t,
            handleOpen: (id) => {
                setDataOutput(id);
                handleOpen();
            },
            onRemoveDataOutput: handleRemoveDataOutput,
            onRemoveDatasetFromDataOutput: handleRemoveDatasetFromDataOutput,
            isDisabled: !isCurrentUserDataProductOwner,
            //isLoading: () => {},//isRemovingDataOutputFromDataProduct,
        });
    }, [t, handleRemoveDataOutput, handleRemoveDatasetFromDataOutput, handleOpen, isCurrentUserDataProductOwner]);

    if (!dataProduct) return null;

    return (
        <>
            <Flex className={styles.dataOutputListContainer}>
                <Table<DataOutputsGetContract[0]>
                    loading={isLoadingDataProduct}
                    className={styles.dataOutputListTable}
                    columns={columns}
                    dataSource={dataOutputs}
                    rowKey={({ id }) => id}
                    onChange={onChange}
                    pagination={{
                        ...pagination,
                        position: ['topRight'],
                        simple: true,
                        showTotal: (total, range) =>
                            t('Showing {{range0}}-{{range1}} of {{total}} data outputs', {
                                range0: range[0],
                                range1: range[1],
                                total: total,
                            }),
                        className: styles.pagination,
                    }}
                    rowClassName={styles.tableRow}
                    size={'small'}
                />
            </Flex>
            {isVisible && dataOutput && (
                <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataOutputId={dataOutput} />
            )}
        </>
    );
}
