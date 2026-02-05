import { Button } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { UserPopup } from '@/components/modal/user-popup/user-popup';
import { useModal } from '@/hooks/use-modal';
import { useRequestDataProductRoleAssignmentMutation } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { type UsersGet, useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { Scope } from '@/types/roles';
import styles from './data-product-request-access-button.module.scss';

type Props = {
    dataProductId: string;
    userId: string;
};

export const DataProductRequestAccessButton = ({ dataProductId, userId }: Props) => {
    const { isVisible, handleOpen, handleClose } = useModal();
    const { t } = useTranslation();
    const [requestAccessToDataProduct, { isLoading: isRequestingAccess }] =
        useRequestDataProductRoleAssignmentMutation();
    const { data: { roles: DATA_PRODUCT_ROLES = [] } = {} } = useGetRolesQuery(Scope.DATA_PRODUCT);

    const { data: { users = [] } = {}, isFetching: isFetchingUsers } = useGetUsersQuery();
    const isLoading = isFetchingUsers || isRequestingAccess;

    const userIdsToHide = useMemo(() => {
        return users.filter((user) => user.id !== userId).map((user) => user.id) ?? [];
    }, [users, userId]);

    const handleRequestAccessToDataProduct = useCallback(
        async (user: UsersGet, role_id: string) => {
            try {
                await requestAccessToDataProduct({
                    data_product_id: dataProductId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has requested access to the Data Product'), type: 'success' });
                handleClose();
            } catch (_error) {
                dispatchMessage({ content: t('Failed to request access to the Data Product'), type: 'error' });
            }
        },
        [requestAccessToDataProduct, dataProductId, t, handleClose],
    );

    if (!dataProductId || !userId) return null;

    return (
        <>
            <Button type="primary" className={styles.largeButton} onClick={handleOpen}>
                {t('Join Team')}
            </Button>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isLoading}
                    userIdsToHide={userIdsToHide}
                    roles={DATA_PRODUCT_ROLES}
                    item={{
                        action: handleRequestAccessToDataProduct,
                        label: t('Request Role'),
                    }}
                />
            )}
        </>
    );
};
