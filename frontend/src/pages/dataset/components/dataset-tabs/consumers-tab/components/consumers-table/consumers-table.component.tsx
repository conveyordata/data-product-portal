import { Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { acceptRequest, rejectRequest } from '@/components/pending-access-requests-modal/request-handlers.ts';
import { ReviewRequestModal } from '@/components/pending-access-requests-modal/review-request-modal.tsx';
import { DEFAULT_TABLE_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type OutputPortInputPort,
    useRevokeOutputPortAsInputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';
import styles from './consumers-table.module.scss';
import { getConsumerColumns } from './consumers-table-columns.tsx';

type Props = {
    dataProductId: string;
    outputPortId: string;
    dataProducts: OutputPortInputPort[];
    isLoading?: boolean;
};

export function ConsumersTable({ outputPortId, dataProductId, dataProducts, isLoading }: Props) {
    const { t } = useTranslation();
    const [revokeOutputPortAsInputPort, { isLoading: isRevokingOutputPortAsInputPort }] =
        useRevokeOutputPortAsInputPortMutation();

    const [reviewingOutputPortInputPortId, setReviewingOutputPortInputPortId] = useState<string | null>(null);

    const { data: { pending_actions } = {} } = useGetUserPendingActionsQuery();
    const handlers = usePendingActionHandlers();

    const reviewingPendingAction = pending_actions?.find(
        (action) => 'input_port' in action && action.input_port.id === reviewingOutputPortInputPortId,
    );

    const { isApprovingDataProductLink, isRejectingDataProductLink: isRejectingDataProductLinkFromHandler } =
        usePendingActionHandlers();

    const { data: approve_access } = useCheckAccessQuery(
        {
            resource: outputPortId,
            action: AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
        },
        { skip: !outputPortId },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: outputPortId,
            action: AuthorizationAction.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
        },
        { skip: !outputPortId },
    );
    const canApprove = approve_access?.allowed || false;
    const canRevoke = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataProducts, {
        initialPagination: DEFAULT_TABLE_PAGINATION,
    });

    const onChange: TableProps<OutputPortInputPort>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRevokeDatasetFromDataProduct = useCallback(
        async (consumingDataProductName: string, consumingDataProductId: string) => {
            try {
                await revokeOutputPortAsInputPort({
                    outputPortId: outputPortId,
                    dataProductId,
                    revokeOutputPortAsInputPortRequest: {
                        consuming_data_product_id: consumingDataProductId,
                    },
                }).unwrap();
                dispatchMessage({
                    content: t('Access to Output Port has been revoked for {{name}}', {
                        name: consumingDataProductName,
                    }),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to revoke access to Output Port'),
                    type: 'error',
                });
            }
        },
        [outputPortId, dataProductId, revokeOutputPortAsInputPort, t],
    );

    const columns: TableColumnsType<OutputPortInputPort> = useMemo(() => {
        return getConsumerColumns({
            t,
            outputPortId,
            dataProductLinks: dataProducts,
            onRevokeDataProductDatasetLink: handleRevokeDatasetFromDataProduct,
            isLoading:
                isRevokingOutputPortAsInputPort || isApprovingDataProductLink || isRejectingDataProductLinkFromHandler,
            canApprove: canApprove,
            canRevoke: canRevoke,
            setReviewingOutputPortInputPortId,
        });
    }, [
        t,
        outputPortId,
        dataProducts,
        handleRevokeDatasetFromDataProduct,
        isApprovingDataProductLink,
        isRevokingOutputPortAsInputPort,
        canApprove,
        canRevoke,
        isRejectingDataProductLinkFromHandler,
    ]);

    return (
        <>
            <Table<OutputPortInputPort>
                loading={isLoading}
                columns={columns}
                dataSource={dataProducts}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    placement: ['topEnd'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Data Products', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                    className: styles.pagination,
                }}
                size={'small'}
            />
            {
                <ReviewRequestModal
                    action={reviewingPendingAction}
                    open={reviewingPendingAction !== null}
                    onClose={() => setReviewingOutputPortInputPortId(null)}
                    onAccept={(action, decisionNote) => acceptRequest(action, handlers, decisionNote)}
                    onReject={(action, decisionNote) => rejectRequest(action, handlers, decisionNote)}
                />
            }
        </>
    );
}
