import { Flex, Table, TableColumnsType } from 'antd';
import { UserContract } from '@/types/users';
import { useMemo } from 'react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import styles from './team-table.module.scss';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { DataProductMembershipRole, DataProductUserMembership } from '@/types/data-product-membership';
import { getDataProductUsersTableColumns } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table-columns.tsx';
import {
    useDenyMembershipAccessMutation,
    useGrantMembershipAccessMutation,
    useRemoveMembershipAccessMutation,
    useUpdateMembershipRoleMutation,
} from '@/store/features/data-product-memberships/data-product-memberships-api-slice.ts';
import { getDoesUserHaveAnyDataProductMembership } from '@/utils/data-product-user-role.helper.ts';

type Props = {
    isCurrentUserDataProductOwner: boolean;
    dataProductId: string;
    dataProductUsers: DataProductUserMembership[];
};

function canPerformTeamActions(isCurrentUserDataProductOwner: boolean, userId: string, currentUserId: string) {
    return isCurrentUserDataProductOwner && userId !== currentUserId;
}

export function TeamTable({ isCurrentUserDataProductOwner, dataProductId, dataProductUsers }: Props) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser) as UserContract;
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [updateMembershipRole, { isLoading: isUpdatingMembershipRole }] = useUpdateMembershipRoleMutation();
    const [removeUserFromDataProduct, { isLoading: isRemovingUserFromDataProduct }] =
        useRemoveMembershipAccessMutation();
    const [grantMembershipAccess] = useGrantMembershipAccessMutation();
    const [denyMembershipAccess] = useDenyMembershipAccessMutation();

    const handleRemoveUserAccess = async (membershipId: string) => {
        try {
            if (!dataProduct) return;

            await removeUserFromDataProduct({ membershipId }).unwrap();
            dispatchMessage({ content: t('User access to data product has been removed'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
        }
    };

    const handleGrantAccessToDataProduct = async (membershipId: string) => {
        try {
            await grantMembershipAccess({ membershipId }).unwrap();
            dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to grant user access to the data product'), type: 'error' });
        }
    };

    const handleDenyAccessToDataProduct = async (membershipId: string) => {
        try {
            await denyMembershipAccess({ membershipId }).unwrap();
            dispatchMessage({ content: t('User access to the data product has been denied'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to deny user access to the data product'), type: 'error' });
        }
    };

    const handleRoleChange = async (role: DataProductMembershipRole, membershipId: string) => {
        if (!dataProduct) return;
        try {
            await updateMembershipRole({ dataProductId: dataProduct.id, membershipId, role }).unwrap();
            dispatchMessage({ content: t('User role has been updated'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
        }
    };

    const columns: TableColumnsType<DataProductUserMembership> = useMemo(() => {
        return getDataProductUsersTableColumns({
            t,
            onRemoveMembership: handleRemoveUserAccess,
            onRoleChange: handleRoleChange,
            isRemovingUser: isRemovingUserFromDataProduct,
            dataProductUsers: dataProductUsers,
            canPerformTeamActions: (userId: string) =>
                canPerformTeamActions(isCurrentUserDataProductOwner, userId, currentUser.id),
            isLoading: isLoadingDataProduct || isUpdatingMembershipRole,
            hasCurrentUserMembership: getDoesUserHaveAnyDataProductMembership(currentUser.id, dataProductUsers),
            onRejectMembershipRequest: handleDenyAccessToDataProduct,
            onAcceptMembershipRequest: handleGrantAccessToDataProduct,
        });
    }, [t, isCurrentUserDataProductOwner, currentUser.id, dataProductUsers]);

    if (!dataProduct) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<DataProductUserMembership>
                loading={isLoadingDataProduct || isUpdatingMembershipRole}
                className={styles.teamListTable}
                columns={columns}
                dataSource={dataProductUsers}
                rowKey={({ user }) => user.id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
