import { Button, Flex, Input } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { UserPopup } from '@/components/modal/user-popup/user-popup.tsx';
import { useModal } from '@/hooks/use-modal.tsx';
import { TeamTable } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table.component.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    type DataProductRoleAssignmentResponse,
    useCreateDataProductRoleAssignmentMutation,
    useListDataProductRoleAssignmentsQuery,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import type { UsersGet } from '@/store/api/services/generated/usersApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { Scope } from '@/types/roles';
import styles from './team-tab.module.scss';

function filterUsers(
    users: DataProductRoleAssignmentResponse[],
    searchTerm: string,
): DataProductRoleAssignmentResponse[] {
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
    const { data: dataProduct } = useGetDataProductQuery(dataProductId);
    const { data: roleAssignments, isFetching } = useListDataProductRoleAssignmentsQuery({
        dataProductId: dataProductId,
    });
    const [addUserToDataProduct, { isLoading: isAddingUser }] = useCreateDataProductRoleAssignmentMutation();

    const [searchTerm, setSearchTerm] = useState<string>('');
    const { data: { roles: DATA_PRODUCT_ROLES = [] } = {} } = useGetRolesQuery(Scope.DATA_PRODUCT);

    const filteredUsers = useMemo(() => {
        return filterUsers(roleAssignments?.role_assignments ?? [], searchTerm);
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
        async (user: UsersGet, role_id: string) => {
            try {
                await addUserToDataProduct({
                    data_product_id: dataProductId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the Data Product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant access to the Data Product'), type: 'error' });
            }
        },
        [addUserToDataProduct, dataProductId, t],
    );

    if (!dataProduct || !user) return null;

    return (
        <>
            <Flex vertical gap={'middle'}>
                <Flex gap={'small'}>
                    <Input.Search
                        placeholder={t('Search users by email or name')}
                        allowClear
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <Button type={'primary'} className={styles.formButton} onClick={handleOpen} disabled={!canAddUser}>
                        {t('Add User')}
                    </Button>
                </Flex>
                <TeamTable dataProductId={dataProductId} dataProductUsers={filteredUsers} />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser}
                    userIdsToHide={dataProductUserIds}
                    roles={DATA_PRODUCT_ROLES}
                    item={{
                        action: handleGrantAccessToDataProduct,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
