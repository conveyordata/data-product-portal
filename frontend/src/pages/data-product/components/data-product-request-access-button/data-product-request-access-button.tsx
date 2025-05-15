import { Button } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { UserPopup } from '@/components/modal/user-popup/user-popup';
import { useModal } from '@/hooks/use-modal';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useGetRoleAssignmentQuery,
    useRequestRoleAssignmentMutation,
} from '@/store/features/role-assignments/roles-api-slice';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice';
import { UserContract } from '@/types/users';

import styles from './data-product-request-access-button.module.scss';

type Props = {
    dataProductId: string;
    userId: string;
};

export const DataProductRequestAccessButton = ({ dataProductId, userId }: Props) => {
    const { isVisible, handleOpen, handleClose } = useModal();
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: roleAssignments, isFetching: isFetchingRoleAssignments } = useGetRoleAssignmentQuery({
        data_product_id: dataProductId,
        user_id: userId,
    });
    const [requestAccessToDataProduct, { isLoading: isRequestingAccess }] = useRequestRoleAssignmentMutation();
    const { data: DATA_PRODUCT_ROLES } = useGetRolesQuery('data_product');

    const { data: users = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();

    const isLoading = isFetchingRoleAssignments || isFetchingUsers || isRequestingAccess;

    const canRequestProductAccess = useMemo(() => {
        if (!dataProduct || !userId || isLoading || !roleAssignments) return false;

        return roleAssignments.some((assignment) => assignment.user.id === userId) ? false : true;
    }, [dataProduct, userId, isLoading, roleAssignments]);

    const filteredUserIds = useMemo(() => {
        if (canRequestProductAccess) {
            return users.filter((user) => user.id !== userId).map((user) => user.id);
        } else {
            return users.map((user) => user.id);
        }
    }, [users, userId, canRequestProductAccess]);

    const handleRequestAccessToDataProduct = useCallback(
        async (user: UserContract, role_id: string) => {
            try {
                await requestAccessToDataProduct({
                    data_product_id: dataProductId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has requested access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to request access to the data product'), type: 'error' });
            }
        },
        [requestAccessToDataProduct, dataProductId, t],
    );

    if (!dataProduct || !userId) return null;

    return (
        <>
            <Button
                type="primary"
                className={styles.largeButton}
                onClick={handleOpen}
                disabled={!canRequestProductAccess}
            >
                {t('Join Team')}
            </Button>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isLoading}
                    userIdsToHide={filteredUserIds}
                    roles={DATA_PRODUCT_ROLES || []}
                    item={{
                        action: handleRequestAccessToDataProduct,
                        label: t('Request Role'),
                    }}
                />
            )}
        </>
    );
};
