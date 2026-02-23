import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
    useDecideDataProductRoleAssignmentMutation,
    useDecideOutputPortRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import {
    type ApproveOutputPortAsInputPortApiArg,
    type DenyOutputPortAsInputPortApiArg,
    useApproveOutputPortAsInputPortMutation,
    useDenyOutputPortAsInputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import {
    type ApproveOutputPortTechnicalAssetLinkApiArg,
    type DenyOutputPortTechnicalAssetLinkApiArg,
    useApproveOutputPortTechnicalAssetLinkMutation,
    useDenyOutputPortTechnicalAssetLinkMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DecisionStatus } from '@/types/roles';

export interface DataProductRoleRequest {
    assignment_id: string;
    data_product_id: string;
}

interface DatasetRoleRequest {
    assignment_id: string;
    dataset_id: string;
}

export const usePendingActionHandlers = () => {
    const { t } = useTranslation();

    const [approveDataProductLink, { isLoading: isApprovingDataProductLink }] =
        useApproveOutputPortAsInputPortMutation();
    const [rejectDataProductLink, { isLoading: isRejectingDataProductLink }] = useDenyOutputPortAsInputPortMutation();
    const [approveDataOutputLink, { isLoading: isApprovingDataOutputLink }] =
        useApproveOutputPortTechnicalAssetLinkMutation();
    const [rejectDataOutputLink, { isLoading: isRejectingDataOutputLink }] =
        useDenyOutputPortTechnicalAssetLinkMutation();
    const [decideDataProductRoleAssignment, { isLoading: isDecidingDataProductRoleAssignment }] =
        useDecideDataProductRoleAssignmentMutation();
    const [decideDatasetRoleAssignment, { isLoading: isDecidingDatasetRoleAssignment }] =
        useDecideOutputPortRoleAssignmentMutation();

    const handleAcceptDataProductDatasetLink = useCallback(
        async (request: ApproveOutputPortAsInputPortApiArg) => {
            try {
                await approveDataProductLink(request).unwrap();
                dispatchMessage({
                    content: t('Output Port request has been successfully approved'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to approve Data Product Output Port link'),
                    type: 'error',
                });
            }
        },
        [approveDataProductLink, t],
    );

    const handleRejectDataProductDatasetLink = useCallback(
        async (request: DenyOutputPortAsInputPortApiArg) => {
            try {
                await rejectDataProductLink(request).unwrap();
                dispatchMessage({
                    content: t('Output Port access request has been successfully rejected'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to reject Data Product Output Port link'),
                    type: 'error',
                });
            }
        },
        [rejectDataProductLink, t],
    );

    const handleAcceptDataOutputDatasetLink = useCallback(
        async (request: ApproveOutputPortTechnicalAssetLinkApiArg) => {
            try {
                await approveDataOutputLink(request).unwrap();
                dispatchMessage({
                    content: t('Output Port request has been successfully approved'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to approve Technical Asset Output Port link'),
                    type: 'error',
                });
            }
        },
        [approveDataOutputLink, t],
    );

    const handleRejectDataOutputDatasetLink = useCallback(
        async (request: DenyOutputPortTechnicalAssetLinkApiArg) => {
            try {
                await rejectDataOutputLink(request).unwrap();
                dispatchMessage({
                    content: t('Output Port access request has been successfully rejected'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to reject Technical Asset Output Port link'),
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
                    id: request.assignment_id,
                    decideDataProductRoleAssignment: {
                        decision: DecisionStatus.Approved,
                    },
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the Data Product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the Data Product'), type: 'error' });
            }
        },
        [decideDataProductRoleAssignment, t],
    );

    const handleDenyAccessToDataProduct = useCallback(
        async (request: DataProductRoleRequest) => {
            try {
                await decideDataProductRoleAssignment({
                    id: request.assignment_id,
                    decideDataProductRoleAssignment: {
                        decision: DecisionStatus.Denied,
                    },
                }).unwrap();
                dispatchMessage({ content: t('User access to the Data Product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the Data Product'), type: 'error' });
            }
        },
        [decideDataProductRoleAssignment, t],
    );

    const handleGrantAccessToDataset = useCallback(
        async (request: DatasetRoleRequest) => {
            try {
                await decideDatasetRoleAssignment({
                    id: request.assignment_id,
                    decideOutputPortRoleAssignment: {
                        decision: DecisionStatus.Approved,
                    },
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the Data Product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the Data Product'), type: 'error' });
            }
        },
        [decideDatasetRoleAssignment, t],
    );

    const handleDenyAccessToDataset = useCallback(
        async (request: DatasetRoleRequest) => {
            try {
                await decideDatasetRoleAssignment({
                    id: request.assignment_id,
                    decideOutputPortRoleAssignment: {
                        decision: DecisionStatus.Denied,
                    },
                }).unwrap();
                dispatchMessage({ content: t('User access to the Data Product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the Data Product'), type: 'error' });
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
