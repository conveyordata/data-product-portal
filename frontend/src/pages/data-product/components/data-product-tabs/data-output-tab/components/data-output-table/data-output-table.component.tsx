import { Flex, Table, type TableColumnsType } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import styles from './data-output-table.module.scss';
import { getDataProductDataOutputsColumns } from './data-output-table-columns.tsx';
import { DataOutputsGetContract } from '@/types/data-output';
import { useModal } from '@/hooks/use-modal.tsx';
import { AddDatasetPopup } from '../add-dataset-popup/add-dataset-popup.tsx';
import {
    useRemoveDataOutputMutation,
    useRemoveDatasetFromDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

type Props = {
    dataProductId: string;
    dataOutputs: DataOutputsGetContract;
};

export function DataOutputTable({ dataProductId, dataOutputs }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    const [removeDatasetFromDataOutput] = useRemoveDatasetFromDataOutputMutation();
    const [removeDataOutput] = useRemoveDataOutputMutation();

    const [dataOutput, setDataOutput] = useState<string | undefined>(undefined);
    const { isVisible, handleOpen, handleClose } = useModal();

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
            //isDisabled: !isCurrentDataProductOwner,
            //isLoading: () => {},//isRemovingDataOutputFromDataProduct,
        });
    }, [t, handleRemoveDataOutput, handleRemoveDatasetFromDataOutput, handleOpen]);

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
                    pagination={false}
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
