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
} from '@/store/features/role-assignments/roles-api-slice';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DataProductMembershipRole } from '@/types/data-product-membership';
import { RoleAssignmentContract } from '@/types/roles/role.contract';
import { SearchForm } from '@/types/shared';
import { UserContract } from '@/types/users';
import { getIsDataProductOwner } from '@/utils/data-product-user-role.helper.ts';

import styles from './team-tab.module.scss';

type Props = {
    dataProductId: string;
};

function filterUsers(users: RoleAssignmentContract[], searchTerm: string) {
    if (!searchTerm) return users;
    if (!users) return [];

    console.log(users);
    console.log(
        users.filter((membership) => {
            const searchString = searchTerm.toLowerCase();
            return (
                membership?.user?.email?.toLowerCase()?.includes(searchString) ||
                membership?.user?.first_name?.toLowerCase()?.includes(searchString) ||
                membership?.user?.last_name?.toLowerCase()?.includes(searchString)
            );
        }) ?? [],
    );
    return (
        users.filter((membership) => {
            const searchString = searchTerm.toLowerCase();
            return (
                membership?.user?.email?.toLowerCase()?.includes(searchString) ||
                membership?.user?.first_name?.toLowerCase()?.includes(searchString) ||
                membership?.user?.last_name?.toLowerCase()?.includes(searchString)
            );
        }) ?? []
    );
}

export function TeamTab({ dataProductId }: Props) {
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: roleAssignments, isFetching } = useGetRoleAssignmentQuery({
        data_product_id: dataProductId,
        user_id: undefined,
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

    const canAddUserNew = access?.allowed || false;

    const isDataProductOwner = useMemo(() => {
        if (!dataProduct || !user) return false;

        return getIsDataProductOwner(dataProduct, user.id) || user.is_admin;
    }, [dataProduct, user]);

    const handleGrantAccessToDataProduct = useCallback(
        async (user: UserContract) => {
            try {
                // Use Member as default initial role (for now)
                const role_id =
                    DATA_PRODUCT_ROLES?.find((role) => role.name.toLowerCase() === DataProductMembershipRole.Member)
                        ?.id || '';

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
        [addUserToDataProduct, dataProductId, t, DATA_PRODUCT_ROLES],
    );

    if (!dataProduct || !user) return null;

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    form={searchForm}
                    formItemProps={{ initialValue: '' }}
                    placeholder={t('Search users by email or name')}
                    actionButton={
                        <Button
                            disabled={!(canAddUserNew || isDataProductOwner)}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add User')}
                        </Button>
                    }
                />
                <TeamTable
                    isCurrentUserDataProductOwner={isDataProductOwner}
                    dataProductId={dataProductId}
                    dataProductUsers={filteredUsers}
                />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser}
                    userIdsToHide={dataProductUserIds}
                    item={{
                        action: handleGrantAccessToDataProduct,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
