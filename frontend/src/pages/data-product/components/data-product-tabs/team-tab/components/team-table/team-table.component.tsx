import { TeamOutlined } from '@ant-design/icons';
import { Flex, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { EmptyStateFilter, EmptyStateQuery } from '@/components/empty-state/empty-state.component.tsx';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getDataProductTeamTableColumns } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table-columns';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type DataProductRoleAssignmentResponse,
    useDeleteDataProductRoleAssignmentMutation,
    useModifyDataProductRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { dispatchMessage } from '@/utils/feedback.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import styles from './team-table.module.scss';

type Props = {
    dataProductId: string;
    assignments: DataProductRoleAssignmentResponse[];
    filteredAssignments: DataProductRoleAssignmentResponse[];
    roleAssignmentsQuery: EmptyStateQuery;
    filter?: EmptyStateFilter;
};
export function TeamTable({ dataProductId, assignments, filteredAssignments, roleAssignmentsQuery, filter }: Props) {
    const { t } = useTranslation();
    const [deleteRoleAssignment, { isLoading: isRemoving }] = useDeleteDataProductRoleAssignmentMutation();
    const [updateRoleAssignment, { isLoading: isUpdating }] = useModifyDataProductRoleAssignmentMutation();

    const { handleGrantAccessToDataProduct, handleDenyAccessToDataProduct, isDecidingDataProductRoleAssignment } =
        usePendingActionHandlers();
    const isSaving = isRemoving || isUpdating || isDecidingDataProductRoleAssignment || roleAssignmentsQuery.isFetching;

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

    const canApprove = approve_access?.allowed || false;
    const canEdit = edit_access?.allowed || false;
    const canRemove = remove_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(filteredAssignments, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataProductRoleAssignmentResponse>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveAccess = useCallback(
        async (id: string) => {
            try {
                await deleteRoleAssignment(id).unwrap();
                dispatchMessage({ content: t('Data Product role has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove Data Product role'), type: 'error' });
            }
        },
        [deleteRoleAssignment, t],
    );

    const handleRoleChange = useCallback(
        async (role: Role, assignmentId: string) => {
            try {
                await updateRoleAssignment({
                    id: assignmentId,
                    modifyDataProductRoleAssignment: {
                        role_id: role.id,
                    },
                }).unwrap();
                dispatchMessage({ content: t('Data Product role has been updated'), type: 'success' });
            } catch (_error) {
                console.error(_error);
                dispatchMessage({ content: t('Failed to update Data Product role'), type: 'error' });
            }
        },
        [t, updateRoleAssignment],
    );

    const handleAcceptAccessRequest = useCallback(
        async (id: string) => {
            await handleGrantAccessToDataProduct({ assignment_id: id, data_product_id: dataProductId });
        },
        [dataProductId, handleGrantAccessToDataProduct],
    );

    const handleRejectAccessRequest = useCallback(
        async (id: string) => {
            await handleDenyAccessToDataProduct({ assignment_id: id, data_product_id: dataProductId });
        },
        [dataProductId, handleDenyAccessToDataProduct],
    );

    const columns: TableColumnsType<DataProductRoleAssignmentResponse> = useMemo(() => {
        return getDataProductTeamTableColumns({
            t,
            assignments,
            onRemoveAccess: handleRemoveAccess,
            onRejectAccessRequest: handleRejectAccessRequest,
            onAcceptAccessRequest: handleAcceptAccessRequest,
            onRoleChange: handleRoleChange,
            isSaving,
            canApprove,
            canEdit,
            canRemove,
        });
    }, [
        t,
        handleRemoveAccess,
        handleRoleChange,
        isSaving,
        assignments,
        canEdit,
        canRemove,
        canApprove,
        handleAcceptAccessRequest,
        handleRejectAccessRequest,
    ]);

    return (
        <Flex className={styles.teamListContainer}>
            <ListTable<DataProductRoleAssignmentResponse>
                query={roleAssignmentsQuery}
                dataSource={filteredAssignments}
                columns={columns}
                subject={t('team members')}
                emptyState={{
                    icon: <TeamOutlined />,
                    title: t('No team members yet'),
                    description: t(
                        'Assign roles to users, groups or machine users to give them access to this Data Product.',
                    ),
                }}
                onChange={onChange}
                filter={filter}
                className={styles.teamListTable}
                rowKey={({ id }) => id}
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
                size="small"
            />
        </Flex>
    );
}
