import { Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getDataProductUsersTableColumns } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table-columns';
import {
    type DataProductRoleAssignmentResponse,
    useDeleteDataProductRoleAssignmentMutation,
    useModifyDataProductRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import styles from './team-table.module.scss';

type Props = {
    dataProductId: string;
    dataProductUsers: DataProductRoleAssignmentResponse[];
};
export function TeamTable({ dataProductId, dataProductUsers }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [deleteRoleAssignment, { isLoading: isRemovingUserFromDataProduct }] =
        useDeleteDataProductRoleAssignmentMutation();
    const [updateRoleAssignment] = useModifyDataProductRoleAssignmentMutation();

    const { handleGrantAccessToDataProduct, handleDenyAccessToDataProduct } = usePendingActionHandlers();

    const { data: approve_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__APPROVE_USER_REQUEST,
        },
        { skip: !dataProductId },
    );
    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_USER,
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

    const canApproveUser = approve_access?.allowed || false;
    const canEditUser = edit_access?.allowed || false;
    const canRemoveUser = remove_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataProductUsers, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataProductRoleAssignmentResponse>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveUserAccess = useCallback(
        async (id: string) => {
            try {
                if (!dataProduct) return;

                await deleteRoleAssignment(id).unwrap();
                dispatchMessage({ content: t('User access to Data Product has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
            }
        },
        [dataProduct, deleteRoleAssignment, t],
    );

    const handleRoleChange = useCallback(
        async (role: Role, assignmentId: string) => {
            if (!dataProduct) return;
            try {
                await updateRoleAssignment({
                    id: assignmentId,
                    modifyDataProductRoleAssignment: {
                        role_id: role.id,
                    },
                }).unwrap();
                dispatchMessage({ content: t('User role has been updated'), type: 'success' });
            } catch (_error) {
                console.error(_error);
                dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
            }
        },
        [dataProduct, t, updateRoleAssignment],
    );

    const handleAcceptAccessRequest = useCallback(
        async (id: string) => {
            if (!dataProduct) return;
            await handleGrantAccessToDataProduct({ assignment_id: id, data_product_id: dataProduct.id });
        },
        [dataProduct, handleGrantAccessToDataProduct],
    );

    const handleRejectAccessRequest = useCallback(
        async (id: string) => {
            if (!dataProduct) return;
            await handleDenyAccessToDataProduct({ assignment_id: id, data_product_id: dataProduct.id });
        },
        [dataProduct, handleDenyAccessToDataProduct],
    );

    const columns: TableColumnsType<DataProductRoleAssignmentResponse> = useMemo(() => {
        return getDataProductUsersTableColumns({
            t,
            dataProductUsers: dataProductUsers,
            onRemoveUserAccess: handleRemoveUserAccess,
            onRejectAccessRequest: handleRejectAccessRequest,
            onAcceptAccessRequest: handleAcceptAccessRequest,
            onRoleChange: handleRoleChange,
            isRemovingUser: isRemovingUserFromDataProduct,
            isLoading: isLoadingDataProduct,
            canApprove: canApproveUser,
            canEdit: canEditUser,
            canRemove: canRemoveUser,
        });
    }, [
        t,
        handleRemoveUserAccess,
        handleRoleChange,
        isRemovingUserFromDataProduct,
        dataProductUsers,
        isLoadingDataProduct,
        canEditUser,
        canRemoveUser,
        canApproveUser,
        handleAcceptAccessRequest,
        handleRejectAccessRequest,
    ]);

    if (!dataProduct) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<DataProductRoleAssignmentResponse>
                loading={isLoadingDataProduct}
                className={styles.teamListTable}
                columns={columns}
                dataSource={dataProductUsers}
                rowKey={({ user }) => user.id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    placement: ['topEnd'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} team members', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
