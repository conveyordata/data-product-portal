import { Flex, Table, TableColumnsType, TableProps } from 'antd';
import { useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getDataProductUsersTableColumns } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table-columns.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import {
    useDenyMembershipAccessMutation,
    useGrantMembershipAccessMutation,
    useRemoveMembershipAccessMutation,
    useUpdateMembershipRoleMutation,
} from '@/store/features/data-product-memberships/data-product-memberships-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DataProductMembershipRole, DataProductUserMembership } from '@/types/data-product-membership';
import { UserContract } from '@/types/users';
import { getDoesUserHaveAnyDataProductMembership } from '@/utils/data-product-user-role.helper.ts';

import styles from './team-table.module.scss';

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

    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_USER,
        },
        { skip: !dataProductId },
    );
    const { data: approve_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__APPROVE_USER_REQUEST,
        },
        { skip: !dataProductId },
    );
    const { data: remove_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__DELETE_USER,
        },
        { skip: !dataProductId },
    );

    const canApproveUserNew = approve_access?.allowed || false;
    const canEditUserNew = edit_access?.allowed || false;
    const canRemoveUserNew = remove_access?.allowed || false;

    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataProductUserMembership>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    useEffect(() => {
        resetPagination();
    }, [dataProductUsers, resetPagination]);

    const handleRemoveUserAccess = useCallback(
        async (membershipId: string) => {
            try {
                if (!dataProduct) return;

                await removeUserFromDataProduct({ membershipId }).unwrap();
                dispatchMessage({ content: t('User access to data product has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
            }
        },
        [dataProduct, removeUserFromDataProduct, t],
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

    const handleRoleChange = useCallback(
        async (role: DataProductMembershipRole, membershipId: string) => {
            if (!dataProduct) return;
            try {
                await updateMembershipRole({ dataProductId: dataProduct.id, membershipId, role }).unwrap();
                dispatchMessage({ content: t('User role has been updated'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
            }
        },
        [dataProduct, t, updateMembershipRole],
    );

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
            canEdit: canEditUserNew,
            canRemove: canRemoveUserNew,
            canApprove: canApproveUserNew,
        });
    }, [
        t,
        handleRemoveUserAccess,
        handleRoleChange,
        isRemovingUserFromDataProduct,
        dataProductUsers,
        isLoadingDataProduct,
        isUpdatingMembershipRole,
        currentUser.id,
        handleDenyAccessToDataProduct,
        handleGrantAccessToDataProduct,
        isCurrentUserDataProductOwner,
        canEditUserNew,
        canRemoveUserNew,
        canApproveUserNew,
    ]);

    if (!dataProduct) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<DataProductUserMembership>
                loading={isLoadingDataProduct || isUpdatingMembershipRole}
                className={styles.teamListTable}
                columns={columns}
                dataSource={dataProductUsers}
                rowKey={({ user }) => user.id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    simple: true,
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} team members', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
