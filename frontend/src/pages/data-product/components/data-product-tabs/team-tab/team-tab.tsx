import { Button, Flex, Form } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Searchbar } from '@/components/form';
import { UserPopup } from '@/components/modal/user-popup/user-popup.tsx';
import { useModal } from '@/hooks/use-modal.tsx';
import { TeamTable } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table.component.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useCreateRoleAssignmentMutation,
    useGetRoleAssignmentQuery,
} from '@/store/features/role-assignments/data-product-roles-api-slice';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DataProductRoleAssignmentContract } from '@/types/roles/role.contract';
import type { SearchForm } from '@/types/shared';
import type { UserContract } from '@/types/users';

import styles from './team-tab.module.scss';

function filterUsers(
    users: DataProductRoleAssignmentContract[],
    searchTerm: string,
): DataProductRoleAssignmentContract[] {
    if (!searchTerm) return users;

    const searchString = searchTerm.toLowerCase();
    return users.filter((assignment) => {
        const user = assignment?.user;
        return (
            user?.email?.toLowerCase()?.includes(searchString) ||
            user?.first_name?.toLowerCase()?.includes(searchString) ||
            user?.last_name?.toLowerCase()?.includes(searchString)
        );
    });
}

type Props = {
    dataProductId: string;
};
export function TeamTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: roleAssignments, isFetching } = useGetRoleAssignmentQuery({
        data_product_id: dataProductId,
    });
    const [addUserToDataProduct, { isLoading: isAddingUser }] = useCreateRoleAssignmentMutation();

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const { data: DATA_PRODUCT_ROLES } = useGetRolesQuery('data_product');

    const filteredUsers = useMemo(() => {
        return filterUsers(roleAssignments ?? [], searchTerm);
    }, [searchTerm, roleAssignments]);
    const dataProductUserIds = useMemo(() => filteredUsers.map((user) => user.user.id), [filteredUsers]);

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_USER,
        },
        { skip: !dataProductId },
    );

    const canAddUser = access?.allowed || false;

    const handleGrantAccessToDataProduct = useCallback(
        async (user: UserContract, role_id: string) => {
            try {
                await addUserToDataProduct({
                    data_product_id: dataProductId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant access to the data product'), type: 'error' });
            }
        },
        [addUserToDataProduct, dataProductId, t],
    );

    if (!dataProduct || !user) return null;

    return (
        <>
            <Flex vertical className={`${styles.container} ${filteredUsers.length === 0 && styles.paginationGap}`}>
                <Searchbar
                    form={searchForm}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    placeholder={t('Search users by email or name')}
                    actionButton={
                        <Button
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                            disabled={!canAddUser}
                        >
                            {t('Add User')}
                        </Button>
                    }
                />
                <TeamTable dataProductId={dataProductId} dataProductUsers={filteredUsers} />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser}
                    userIdsToHide={dataProductUserIds}
                    roles={DATA_PRODUCT_ROLES || []}
                    item={{
                        action: handleGrantAccessToDataProduct,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
