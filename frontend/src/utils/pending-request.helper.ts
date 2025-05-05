import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import {
    useApproveDataOutputLinkMutation,
    useRejectDataOutputLinkMutation,
} from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import {
    useDenyMembershipAccessMutation,
    useGrantMembershipAccessMutation,
} from '@/store/features/data-product-memberships/data-product-memberships-api-slice';
import {
    useApproveDataProductLinkMutation,
    useRejectDataProductLinkMutation,
} from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';

export const usePendingActionHandlers = () => {
    const { t } = useTranslation();

    const [approveDataProductLink, { isLoading: isApprovingDataProductLink }] = useApproveDataProductLinkMutation();
    const [rejectDataProductLink, { isLoading: isRejectingDataProductLink }] = useRejectDataProductLinkMutation();
    const [approveDataOutputLink, { isLoading: isApprovingDataOutputLink }] = useApproveDataOutputLinkMutation();
    const [rejectDataOutputLink, { isLoading: isRejectingDataOutputLink }] = useRejectDataOutputLinkMutation();
    const [grantMembershipAccess, { isLoading: isGrantingMembershipAccess }] = useGrantMembershipAccessMutation();
    const [denyMembershipAccess, { isLoading: isDenyingMembershipAccess }] = useDenyMembershipAccessMutation();

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
        async (membershipId: string) => {
            try {
                await grantMembershipAccess({ membershipId }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the data product'), type: 'error' });
            }
        },
        [grantMembershipAccess, t],
    );

    const handleDenyAccessToDataProduct = useCallback(
        async (membershipId: string) => {
            try {
                await denyMembershipAccess({ membershipId }).unwrap();
                dispatchMessage({ content: t('User access to the data product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the data product'), type: 'error' });
            }
        },
        [denyMembershipAccess, t],
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
        isGrantingMembershipAccess,
        isDenyingMembershipAccess,
    };
};
