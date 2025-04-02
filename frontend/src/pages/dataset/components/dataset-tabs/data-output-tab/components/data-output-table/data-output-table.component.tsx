import { Flex, Table, type TableColumnsType } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDataOutputDatasetLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { useApproveDataOutputLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { useRejectDataOutputLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset/data-output-dataset-link.contract.ts';
import type { DataOutputLink } from '@/types/dataset';

import styles from './data-output-table.module.scss';
import { getDatasetDataProductsColumns } from './data-output-table-columns.tsx';

type Props = {
    isCurrentDatasetOwner: boolean;
    datasetId: string;
    dataOutputs: DataOutputLink[];
    currentUserId?: string;
    isLoading?: boolean;
};

export function DataOutputTable({ isCurrentDatasetOwner, datasetId, dataOutputs, isLoading }: Props) {
    const { t } = useTranslation();
    const [approveDataOutputLink, { isLoading: isApprovingLink }] = useApproveDataOutputLinkMutation();
    const [rejectDataOutputLink, { isLoading: isRejectingLink }] = useRejectDataOutputLinkMutation();
    const [removeDatasetFromDataOutput, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveDataOutputDatasetLinkMutation();

    const { data: accept_access } = useCheckAccessQuery(
        {
            object_id: datasetId,
            action: AuthorizationAction.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
        },
        {
            skip: !datasetId,
        },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            object_id: datasetId,
            action: AuthorizationAction.DATASET__REVOKE_DATA_OUTPUT_LINK,
        },
        {
            skip: !datasetId,
        },
    );
    const canAcceptNew = accept_access?.access || false;
    const canRevokeNew = revoke_access?.access || false;

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

    const handleAcceptDataOutputDatasetLink = useCallback(
        async (request: DataOutputDatasetLinkRequest) => {
            try {
                await approveDataOutputLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset request has been successfully approved'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to approve data output dataset link'),
                    type: 'error',
                });
            }
        },
        [approveDataOutputLink, t],
    );

    const handleRejectDataOutputDatasetLink = useCallback(
        async (request: DataOutputDatasetLinkRequest) => {
            try {
                await rejectDataOutputLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset access request has been successfully rejected'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to reject data output dataset link'),
                    type: 'error',
                });
            }
        },
        [rejectDataOutputLink, t],
    );

    const columns: TableColumnsType<DataOutputLink> = useMemo(() => {
        return getDatasetDataProductsColumns({
            onRemoveDataOutputDatasetLink: handleRemoveDatasetFromDataOutput,
            t,
            isDisabled: !isCurrentDatasetOwner,
            canAcceptNew: canAcceptNew,
            canRevokeNew: canRevokeNew,
            isLoading: isRemovingDatasetFromDataProduct || isRejectingLink || isApprovingLink,
            isCurrentDatasetOwner,
            onRejectDataOutputDatasetLink: handleRejectDataOutputDatasetLink,
            onAcceptDataOutputDatasetLink: handleAcceptDataOutputDatasetLink,
        });
    }, [
        handleRemoveDatasetFromDataOutput,
        t,
        isCurrentDatasetOwner,
        isRemovingDatasetFromDataProduct,
        isRejectingLink,
        isApprovingLink,
        handleRejectDataOutputDatasetLink,
        handleAcceptDataOutputDatasetLink,
        canAcceptNew,
        canRevokeNew,
    ]);

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DataOutputLink>
                loading={isLoading}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={dataOutputs}
                rowKey={({ id }) => id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
