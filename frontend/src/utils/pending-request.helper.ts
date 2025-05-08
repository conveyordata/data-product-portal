import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import {
    useApproveDataOutputLinkMutation,
    useRejectDataOutputLinkMutation,
} from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import {
    useApproveDataProductLinkMutation,
    useRejectDataProductLinkMutation,
} from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { useDecideRoleAssignmentMutation } from '@/store/features/role-assignments/roles-api-slice';
import { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';
import { DecisionStatus } from '@/types/roles';

export const usePendingActionHandlers = () => {
    const { t } = useTranslation();

    const [approveDataProductLink, { isLoading: isApprovingDataProductLink }] = useApproveDataProductLinkMutation();
    const [rejectDataProductLink, { isLoading: isRejectingDataProductLink }] = useRejectDataProductLinkMutation();
    const [approveDataOutputLink, { isLoading: isApprovingDataOutputLink }] = useApproveDataOutputLinkMutation();
    const [rejectDataOutputLink, { isLoading: isRejectingDataOutputLink }] = useRejectDataOutputLinkMutation();
    const [decideroleAssignment, { isLoading: isDecidingRoleAssignment }] = useDecideRoleAssignmentMutation();

    const handleAcceptDataProductDatasetLink = useCallback(
        async (request: DataProductDatasetLinkRequest) => {
            try {
                await approveDataProductLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset request has been successfully approved'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to approve data product dataset link'),
                    type: 'error',
                });
            }
        },
        [approveDataProductLink, t],
    );

    const handleRejectDataProductDatasetLink = useCallback(
        async (request: DataProductDatasetLinkRequest) => {
            try {
                await rejectDataProductLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset access request has been successfully rejected'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to reject data product dataset link'),
                    type: 'error',
                });
            }
        },
        [rejectDataProductLink, t],
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

    const handleGrantAccessToDataProduct = useCallback(
        async (assignment_id: string) => {
            try {
                await decideroleAssignment({
                    role_assignment_id: assignment_id,
                    decision_status: DecisionStatus.Approved,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the data product'), type: 'error' });
            }
        },
        [decideroleAssignment, t],
    );

    const handleDenyAccessToDataProduct = useCallback(
        async (assignment_id: string) => {
            try {
                await decideroleAssignment({
                    role_assignment_id: assignment_id,
                    decision_status: DecisionStatus.Denied,
                }).unwrap();
                dispatchMessage({ content: t('User access to the data product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the data product'), type: 'error' });
            }
        },
        [decideroleAssignment, t],
    );

    return {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        handleGrantAccessToDataProduct,
        handleDenyAccessToDataProduct,

        isApprovingDataProductLink,
        isRejectingDataProductLink,
        isApprovingDataOutputLink,
        isRejectingDataOutputLink,
        isDecidingRoleAssignment,
    };
};
