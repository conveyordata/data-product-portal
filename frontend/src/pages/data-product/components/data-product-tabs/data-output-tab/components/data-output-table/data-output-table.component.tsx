import { Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputsGetContract } from '@/types/data-output';

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
        });
    }, [t, deleteDataOutput, handleRemoveDataOutput]);

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
            </Flex>
        </>
    );
}
