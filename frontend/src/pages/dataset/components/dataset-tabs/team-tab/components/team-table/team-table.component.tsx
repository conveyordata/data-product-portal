import { Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useDeleteDatasetRoleAssignmentMutation,
    useUpdateDatasetRoleAssignmentMutation,
} from '@/store/features/role-assignments/dataset-roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DatasetRoleAssignmentContract, RoleContract } from '@/types/roles/role.contract';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

import { getDatasetTeamColumns } from './team-table-columns';
import styles from './team-table.module.scss';

type Props = {
    datasetId: string;
    datasetUsers: DatasetRoleAssignmentContract[];
};
export function TeamTable({ datasetId, datasetUsers }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isLoading: isFetchingDataset } = useGetDatasetByIdQuery(datasetId);
    const [deleteRoleAssignment, { isLoading: isRemovingUser }] = useDeleteDatasetRoleAssignmentMutation();
    const [updateRoleAssignment] = useUpdateDatasetRoleAssignmentMutation();

    const { handleGrantAccessToDataset, handleDenyAccessToDataset } = usePendingActionHandlers();

    const { data: approve_access } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.DATASET__APPROVE_USER_REQUEST,
    });
    const { data: edit_access } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.DATASET__UPDATE_USER,
    });
    const { data: remove_access } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.DATASET__DELETE_USER,
    });

    const canApproveUser = approve_access?.allowed || false;
    const canEditUser = edit_access?.allowed || false;
    const canRemoveUser = remove_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(datasetUsers, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DatasetRoleAssignmentContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveUserAccess = useCallback(
        async (id: string) => {
            try {
                if (!dataset) return;

                await deleteRoleAssignment({ role_assignment_id: id, dataset_id: dataset.id }).unwrap();
                dispatchMessage({ content: t('User access to dataset has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
            }
        },
        [dataset, deleteRoleAssignment, t],
    );

    const handleRoleChange = useCallback(
        async (role: RoleContract, assignmentId: string) => {
            if (!dataset) return;
            try {
                await updateRoleAssignment({
                    role_assignment_id: assignmentId,
                    role_id: role.id,
                    dataset_id: dataset.id,
                }).unwrap();
                dispatchMessage({ content: t('User role has been updated'), type: 'success' });
            } catch (_error) {
                console.log(_error);
                dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
            }
        },
        [dataset, t, updateRoleAssignment],
    );

    const handleAcceptAccessRequest = useCallback(
        async (id: string) => {
            if (!dataset) return;
            await handleGrantAccessToDataset({ assignment_id: id, dataset_id: dataset.id });
        },
        [dataset, handleGrantAccessToDataset],
    );

    const handleRejectAccessRequest = useCallback(
        async (id: string) => {
            if (!dataset) return;
            await handleDenyAccessToDataset({ assignment_id: id, dataset_id: dataset.id });
        },
        [dataset, handleDenyAccessToDataset],
    );

    const columns: TableColumnsType<DatasetRoleAssignmentContract> = useMemo(() => {
        return getDatasetTeamColumns({
            t,
            datasetUsers: datasetUsers,
            onRemoveUserAccess: handleRemoveUserAccess,
            onRejectAccessRequest: handleRejectAccessRequest,
            onAcceptAccessRequest: handleAcceptAccessRequest,
            onRoleChange: handleRoleChange,
            isRemovingUser: isRemovingUser,
            isLoading: isFetchingDataset,
            canApprove: canApproveUser,
            canEdit: canEditUser,
            canRemove: canRemoveUser,
        });
    }, [
        canApproveUser,
        canEditUser,
        canRemoveUser,
        datasetUsers,
        handleAcceptAccessRequest,
        handleRejectAccessRequest,
        handleRemoveUserAccess,
        handleRoleChange,
        isFetchingDataset,
        isRemovingUser,
        t,
    ]);

    if (!dataset) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<DatasetRoleAssignmentContract>
                loading={isFetchingDataset || isRemovingUser}
                className={styles.teamListTable}
                columns={columns}
                dataSource={datasetUsers}
                rowKey={({ id }) => id}
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
