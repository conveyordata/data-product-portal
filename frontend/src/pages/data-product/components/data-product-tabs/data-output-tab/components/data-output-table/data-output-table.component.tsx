import { Flex, Table, TableColumnsType } from 'antd';
import { useEffect, useMemo, useState } from 'react';
//import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import {
    useGetDataProductByIdQuery,
    //useRemoveDataOutputFromDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import styles from './data-output-table.module.scss';
import { getDataProductDataOutputsColumns } from './data-output-table-columns.tsx';
import { DataOutput } from '@/types/data-output';
import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract.ts';
import { useModal } from '@/hooks/use-modal.tsx';
import { AddDatasetPopup } from '../add-dataset-popup/add-dataset-popup.tsx';

type Props = {
    isCurrentDataProductOwner: boolean;
    dataProductId: string;
    dataOutputs: DataOutputsGetContract[];
};

export function DataOutputTable({ isCurrentDataProductOwner, dataProductId, dataOutputs }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    // const [removeDataOutputFromDataProduct, { isLoading: isRemovingDataOutputFromDataProduct }] =
    //     useRemoveDataOutputFromDataProductMutation();

    // const handleRemoveDataOutputFromDataProduct = async (dataOutputId: string, name: string) => {
    //     try {
    //         await removeDataOutputFromDataProduct({ dataOutputId, dataProductId: dataProductId }).unwrap();
    //         dispatchMessage({
    //             content: t('DataOutput {{name}} has been removed from data product', { name }),
    //             type: 'success',
    //         });
    //     } catch (error) {
    //         console.error('Failed to remove dataOutput from data product', error);
    //     }
    // };

    // const handleCancelDataOutputLinkRequest = async (dataOutputId: string, name: string) => {
    //     try {
    //         await removeDataOutputFromDataProduct({ dataOutputId, dataProductId: dataProductId }).unwrap();
    //         dispatchMessage({
    //             content: t('Request to link dataOutput {{name}} has been cancelled', { name }),
    //             type: 'success',
    //         });
    //     } catch (error) {
    //         console.error('Failed to cancel dataOutput link request', error);
    //     }
    // };
    const [dataOutput, setDataOutput] = useState<string|undefined>(undefined);
    const { isVisible, handleOpen, handleClose } = useModal();

    const columns: TableColumnsType<DataOutputsGetContract> = useMemo(() => {
        return getDataProductDataOutputsColumns({
            t,
            handleOpen: (id) => {
                setDataOutput(id);
                handleOpen()
            }
            //isDisabled: !isCurrentDataProductOwner,
            //isLoading: () => {},//isRemovingDataOutputFromDataProduct,
        });
    }, [dataProductId, t, isCurrentDataProductOwner]);


    if (!dataProduct) return null;

    return (
        <>
        <Flex className={styles.dataOutputListContainer}>
            <Table<DataOutputsGetContract>
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
        {isVisible && dataOutput && <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataOutputId={dataOutput} />}
        </>
    );
}
