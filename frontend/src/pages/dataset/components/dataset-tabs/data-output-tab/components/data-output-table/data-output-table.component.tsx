import { Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import type { TechnicalAssetLink } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useUnlinkOutputPortFromTechnicalAssetMutation } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';
import styles from './data-output-table.module.scss';
import { getDatasetDataProductsColumns } from './data-output-table-columns.tsx';

type Props = {
    dataProductId: string;
    datasetId: string;
    dataOutputs: TechnicalAssetLink[];
    isLoading?: boolean;
};

export function DataOutputTable({ dataProductId, datasetId, dataOutputs, isLoading }: Props) {
    const { t } = useTranslation();
    const {
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        isApprovingDataOutputLink,
        isRejectingDataOutputLink,
    } = usePendingActionHandlers();
    const [removeDatasetFromDataOutput, { isLoading: isRemovingDatasetFromDataProduct }] =
        useUnlinkOutputPortFromTechnicalAssetMutation();

    const { data: accept_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
        },
        { skip: !datasetId },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__REVOKE_TECHNICAL_ASSET_LINK,
        },
        { skip: !datasetId },
    );
    const canAccept = accept_access?.allowed || false;
    const canRevoke = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataOutputs, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<TechnicalAssetLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveDatasetFromDataOutput = useCallback(
        async (dataOutputId: string, name: string) => {
            try {
                await removeDatasetFromDataOutput({
                    outputPortId: datasetId,
                    dataProductId,
                    unLinkTechnicalAssetToOutputPortRequest: { technical_asset_id: dataOutputId },
                }).unwrap();
                dispatchMessage({
                    content: t('Output Port {{name}} has been removed from Technical Asset', { name }),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to remove Output Port from Technical Asset'),
                    type: 'error',
                });
            }
        },
        [datasetId, removeDatasetFromDataOutput, t, dataProductId],
    );

    const columns: TableColumnsType<TechnicalAssetLink> = useMemo(() => {
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
            <Table<TechnicalAssetLink>
                loading={isLoading}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={dataOutputs}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    placement: ['topEnd'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Technical Assets', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
