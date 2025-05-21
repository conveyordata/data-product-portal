import { Button } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { UserPopup } from '@/components/modal/user-popup/user-popup';
import { useModal } from '@/hooks/use-modal';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useCreateRoleAssignmentMutation } from '@/store/features/role-assignments/roles-api-slice';
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
    const [requestAccessToDataProduct, { isLoading: isRequestingAccess }] = useCreateRoleAssignmentMutation();
    const { data: DATA_PRODUCT_ROLES } = useGetRolesQuery('data_product');

    const { data: users = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();

    const isLoading = isFetchingUsers || isRequestingAccess;

    const filteredUserIds = useMemo(() => {
        return users.filter((user) => user.id !== userId).map((user) => user.id);
    }, [users, userId]);

    const handleRequestAccessToDataProduct = useCallback(
        async (user: UserContract, role_id: string) => {
            try {
                await requestAccessToDataProduct({
                    data_product_id: dataProductId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has requested access to the data product'), type: 'success' });
                handleClose();
            } catch (_error) {
                dispatchMessage({ content: t('Failed to request access to the data product'), type: 'error' });
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
