import { Flex, Table, TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import styles from './data-output-table.module.scss';
import { getDatasetDataProductsColumns } from './data-output-table-columns.tsx';
import { DataOutputLink } from '@/types/dataset';
import { useRemoveDataOutputDatasetLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { useApproveDataOutputLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { useRejectDataOutputLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset/data-output-dataset-link.contract.ts';

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

    const handleRemoveDatasetFromDataOutput = async (dataOutputId: string, name: string, datasetLinkId: string) => {
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
    };

    const handleAcceptDataOutputDatasetLink = async (request: DataOutputDatasetLinkRequest) => {
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
    };

    const handleRejectDataOutputDatasetLink = async (request: DataOutputDatasetLinkRequest) => {
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
    };

    const columns: TableColumnsType<DataOutputLink> = useMemo(() => {
        return getDatasetDataProductsColumns({
            onRemoveDataOutputDatasetLink: handleRemoveDatasetFromDataOutput,
            t,
            isDisabled: !isCurrentDatasetOwner,
            isLoading: isRemovingDatasetFromDataProduct || isRejectingLink || isApprovingLink,
            isCurrentDatasetOwner,
            onRejectDataOutputDatasetLink: handleRejectDataOutputDatasetLink,
            onAcceptDataOutputDatasetLink: handleAcceptDataOutputDatasetLink,
        });
    }, [datasetId, t, isCurrentDatasetOwner]);

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
