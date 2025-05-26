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
import { useDecideRoleAssignmentMutation as useDecideDataProductRoleAssignmentMutation } from '@/store/features/role-assignments/data-product-roles-api-slice';
import { useDecideRoleAssignmentMutation as useDecideDatasetRoleAssignmentMutation } from '@/store/features/role-assignments/dataset-roles-api-slice';
import type { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import type { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';
import { DecisionStatus } from '@/types/roles';
import type { DataProductRoleRequest, DatasetRoleRequest } from '@/types/roles/role-assignment-request.ts';

export const usePendingActionHandlers = () => {
    const { t } = useTranslation();

    const [approveDataProductLink, { isLoading: isApprovingDataProductLink }] = useApproveDataProductLinkMutation();
    const [rejectDataProductLink, { isLoading: isRejectingDataProductLink }] = useRejectDataProductLinkMutation();
    const [approveDataOutputLink, { isLoading: isApprovingDataOutputLink }] = useApproveDataOutputLinkMutation();
    const [rejectDataOutputLink, { isLoading: isRejectingDataOutputLink }] = useRejectDataOutputLinkMutation();
    const [decideDataProductRoleAssignment, { isLoading: isDecidingDataProductRoleAssignment }] =
        useDecideDataProductRoleAssignmentMutation();
    const [decideDatasetRoleAssignment, { isLoading: isDecidingDatasetRoleAssignment }] =
        useDecideDatasetRoleAssignmentMutation();

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
        async (request: DataProductRoleRequest) => {
            try {
                await decideDataProductRoleAssignment({
                    role_assignment_id: request.assignment_id,
                    data_product_id: request.data_product_id,
                    decision_status: DecisionStatus.Approved,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the data product'), type: 'error' });
            }
        },
        [decideDataProductRoleAssignment, t],
    );

    const handleDenyAccessToDataProduct = useCallback(
        async (request: DataProductRoleRequest) => {
            try {
                await decideDataProductRoleAssignment({
                    role_assignment_id: request.assignment_id,
                    data_product_id: request.data_product_id,
                    decision_status: DecisionStatus.Denied,
                }).unwrap();
                dispatchMessage({ content: t('User access to the data product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the data product'), type: 'error' });
            }
        },
        [decideDataProductRoleAssignment, t],
    );

    const handleGrantAccessToDataset = useCallback(
        async (request: DatasetRoleRequest) => {
            try {
                await decideDatasetRoleAssignment({
                    role_assignment_id: request.assignment_id,
                    dataset_id: request.dataset_id,
                    decision_status: DecisionStatus.Approved,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the data product'), type: 'error' });
            }
        },
        [decideDatasetRoleAssignment, t],
    );

    const handleDenyAccessToDataset = useCallback(
        async (request: DatasetRoleRequest) => {
            try {
                await decideDatasetRoleAssignment({
                    role_assignment_id: request.assignment_id,
                    dataset_id: request.dataset_id,
                    decision_status: DecisionStatus.Denied,
                }).unwrap();
                dispatchMessage({ content: t('User access to the data product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the data product'), type: 'error' });
            }
        },
        [decideDatasetRoleAssignment, t],
    );

    return {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        handleGrantAccessToDataProduct,
        handleDenyAccessToDataProduct,
        handleGrantAccessToDataset,
        handleDenyAccessToDataset,

        isApprovingDataProductLink,
        isRejectingDataProductLink,
        isApprovingDataOutputLink,
        isRejectingDataOutputLink,
        isDecidingDataProductRoleAssignment,
        isDecidingDatasetRoleAssignment,
    };
};
