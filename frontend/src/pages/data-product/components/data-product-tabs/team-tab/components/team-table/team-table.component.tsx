import { Flex, Table, TableColumnsType, TableProps } from 'antd';
import { useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getDataProductUsersTableColumns } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table-columns.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useDeleteRoleAssignmentMutation,
    useLazyGetRoleAssignmentQuery,
    useUpdateRoleAssignmentMutation,
} from '@/store/features/role-assignments/roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { RoleContract } from '@/types/roles';
import { RoleAssignmentContract } from '@/types/roles/role.contract';
import { UserContract } from '@/types/users';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';

import styles from './team-table.module.scss';

type Props = {
    isCurrentUserDataProductOwner: boolean;
    dataProductId: string;
    dataProductUsers: RoleAssignmentContract[];
};

function canPerformTeamActions(isCurrentUserDataProductOwner: boolean, userId: string, currentUserId: string) {
    return isCurrentUserDataProductOwner && userId !== currentUserId;
}

export function TeamTable({ isCurrentUserDataProductOwner, dataProductId, dataProductUsers }: Props) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser) as UserContract;
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [deleteRoleAssignment, { isLoading: isRemovingUserFromDataProduct }] = useDeleteRoleAssignmentMutation();
    const [updateRoleAssignment] = useUpdateRoleAssignmentMutation();

    const { handleGrantAccessToDataProduct, handleDenyAccessToDataProduct } = usePendingActionHandlers();
    const [lazyGetRolesAssignments] = useLazyGetRoleAssignmentQuery();
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

    const onChange: TableProps<RoleAssignmentContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    useEffect(() => {
        resetPagination();
    }, [dataProductUsers, resetPagination]);

    const handleRemoveUserAccess = useCallback(
        async (id: string) => {
            try {
                if (!dataProduct) return;

                await deleteRoleAssignment(id).unwrap();
                dispatchMessage({ content: t('User access to data product has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
            }
        },
        [dataProduct, deleteRoleAssignment, t],
    );

    const handleRoleChange = useCallback(
        async (role: RoleContract, _: string, userId: string) => {
            if (!dataProduct) return;
            try {
                const roles = await lazyGetRolesAssignments({
                    data_product_id: dataProduct.id,
                    user_id: userId,
                }).unwrap();
                const currentRole = roles[0];
                await updateRoleAssignment({ role_assignment_id: currentRole.id, role_id: role.id }).unwrap();
                dispatchMessage({ content: t('User role has been updated'), type: 'success' });
            } catch (_error) {
                console.log(_error);
                dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
            }
        },
        [dataProduct, t, updateRoleAssignment, lazyGetRolesAssignments],
    );

    const columns: TableColumnsType<RoleAssignmentContract> = useMemo(() => {
        return getDataProductUsersTableColumns({
            t,
            onRemoveMembership: handleRemoveUserAccess,
            onRoleChange: handleRoleChange,
            isRemovingUser: isRemovingUserFromDataProduct,
            dataProductUsers: dataProductUsers,
            canPerformTeamActions: (userId: string) =>
                canPerformTeamActions(isCurrentUserDataProductOwner, userId, currentUser.id),
            isLoading: isLoadingDataProduct,
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
            <Table<RoleAssignmentContract>
                loading={isLoadingDataProduct}
                className={styles.teamListTable}
                columns={columns}
                dataSource={dataProductUsers}
                rowKey={({ user }) => user.id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
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
