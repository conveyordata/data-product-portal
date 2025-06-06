import { Flex, Table, type TableColumnsType, TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDataOutputDatasetLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputLink } from '@/types/dataset';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

import { getDatasetDataProductsColumns } from './data-output-table-columns.tsx';
import styles from './data-output-table.module.scss';

type Props = {
    datasetId: string;
    dataOutputs: DataOutputLink[];
    isLoading?: boolean;
};

export function DataOutputTable({ datasetId, dataOutputs, isLoading }: Props) {
    const { t } = useTranslation();
    const {
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        isApprovingDataOutputLink,
        isRejectingDataOutputLink,
    } = usePendingActionHandlers();
    const [removeDatasetFromDataOutput, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveDataOutputDatasetLinkMutation();

    const { data: accept_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
        },
        { skip: !datasetId },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__REVOKE_DATA_OUTPUT_LINK,
        },
        { skip: !datasetId },
    );
    const canAccept = accept_access?.allowed || false;
    const canRevoke = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataOutputs, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataOutputLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveDatasetFromDataOutput = useCallback(
        async (dataOutputId: string, name: string, datasetLinkId: string) => {
            try {
                await removeDatasetFromDataOutput({ datasetId, dataOutputId, datasetLinkId }).unwrap();
                dispatchMessage({
                    content: t('Dataset {{name}} has been removed from data output', { name }),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to remove dataset from data output'),
                    type: 'error',
                });
            }
        },
        [datasetId, removeDatasetFromDataOutput, t],
    );

    const columns: TableColumnsType<DataOutputLink> = useMemo(() => {
        return getDatasetDataProductsColumns({
            t,
            onAcceptDataOutputDatasetLink: handleAcceptDataOutputDatasetLink,
            onRejectDataOutputDatasetLink: handleRejectDataOutputDatasetLink,
            onRemoveDataOutputDatasetLink: handleRemoveDatasetFromDataOutput,
            isLoading: isRemovingDatasetFromDataProduct || isRejectingDataOutputLink || isApprovingDataOutputLink,
            canAccept: canAccept,
            canRevoke: canRevoke,
        });
    }, [
        t,
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        handleRemoveDatasetFromDataOutput,
        isRemovingDatasetFromDataProduct,
        isRejectingDataOutputLink,
        isApprovingDataOutputLink,
        canAccept,
        canRevoke,
    ]);

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DataOutputLink>
                loading={isLoading}
                className={styles.datasetListTable}
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
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
