import { Flex, Table, TableColumnsType } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { getDatasetUsersTableColumns } from '@/pages/dataset/components/dataset-tabs/team-tab/components/team-table/team-table-columns.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import {
    useDenyMembershipAccessMutation,
    useGrantMembershipAccessMutation,
    useRemoveMembershipAccessMutation,
    useUpdateMembershipRoleMutation,
} from '@/store/features/dataset-memberships/dataset-memberships-api-slice.ts';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DatasetMembershipRole, DatasetUserMembership } from '@/types/dataset-membership';
import { UserContract } from '@/types/users';
import { getDoesUserHaveAnyDatasetMembership } from '@/utils/dataset-user-role.helper.ts';

import styles from './team-table.module.scss';

type Props = {
    isCurrentUserDatasetOwner: boolean;
    datasetId: string;
    datasetUsers: DatasetUserMembership[];
};

function canPerformTeamActions(isCurrentUserDatasetOwner: boolean, userId: string, currentUserId: string) {
    return isCurrentUserDatasetOwner && userId !== currentUserId;
}

export function TeamTable({ isCurrentUserDatasetOwner, datasetId, datasetUsers }: Props) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser) as UserContract;
    const { data: dataset, isLoading: isLoadingDataset } = useGetDatasetByIdQuery(datasetId);
    const [updateMembershipRole, { isLoading: isUpdatingMembershipRole }] = useUpdateMembershipRoleMutation();
    const [removeUserFromDataset, { isLoading: isRemovingUserFromDataset }] = useRemoveMembershipAccessMutation();
    const [grantMembershipAccess] = useGrantMembershipAccessMutation();
    const [denyMembershipAccess] = useDenyMembershipAccessMutation();

    const { data: edit_access } = useCheckAccessQuery(
        {
            object_id: datasetId,
            action: AuthorizationAction.DATA_PRODUCT_UPDATE_USER,
        },
        { skip: !datasetId },
    );
    const { data: approve_access } = useCheckAccessQuery(
        {
            object_id: datasetId,
            action: AuthorizationAction.DATA_PRODUCT_APPROVE_USER_REQUEST,
        },
        { skip: !datasetId },
    );
    const { data: remove_access } = useCheckAccessQuery(
        {
            object_id: datasetId,
            action: AuthorizationAction.DATA_PRODUCT_DELETE_USER,
        },
        { skip: !datasetId },
    );

    const canApproveUserNew = approve_access?.access || false;
    const canEditUserNew = edit_access?.access || false;
    const canRemoveUserNew = remove_access?.access || false;

    const handleRemoveUserAccess = useCallback(
        async (membershipId: string) => {
            try {
                if (!dataset) return;

                await removeUserFromDataset({ membershipId }).unwrap();
                dispatchMessage({ content: t('User access to data product has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
            }
        },
        [dataset, removeUserFromDataset, t],
    );

    const handleGrantAccessToDataset = useCallback(
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

    const handleDenyAccessToDataset = useCallback(
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
        async (role: DatasetMembershipRole, membershipId: string) => {
            if (!dataset) return;
            try {
                await updateMembershipRole({ datasetId: dataset.id, membershipId, role }).unwrap();
                dispatchMessage({ content: t('User role has been updated'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
            }
        },
        [dataset, t, updateMembershipRole],
    );

    const columns: TableColumnsType<DatasetUserMembership> = useMemo(() => {
        return getDatasetUsersTableColumns({
            t,
            onRemoveMembership: handleRemoveUserAccess,
            onRoleChange: handleRoleChange,
            isRemovingUser: isRemovingUserFromDataset,
            datasetUsers: datasetUsers,
            canPerformTeamActions: (userId: string) =>
                canPerformTeamActions(isCurrentUserDatasetOwner, userId, currentUser.id),
            isLoading: isLoadingDataset || isUpdatingMembershipRole,
            hasCurrentUserMembership: getDoesUserHaveAnyDatasetMembership(currentUser.id, datasetUsers),
            onRejectMembershipRequest: handleDenyAccessToDataset,
            onAcceptMembershipRequest: handleGrantAccessToDataset,
            canEdit: canEditUserNew,
            canRemove: canRemoveUserNew,
            canApprove: canApproveUserNew,
        });
    }, [
        t,
        handleRemoveUserAccess,
        handleRoleChange,
        isRemovingUserFromDataset,
        datasetUsers,
        isLoadingDataset,
        isUpdatingMembershipRole,
        currentUser.id,
        handleDenyAccessToDataset,
        handleGrantAccessToDataset,
        isCurrentUserDatasetOwner,
        canEditUserNew,
        canRemoveUserNew,
        canApproveUserNew,
    ]);

    if (!dataset) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<DatasetUserMembership>
                loading={isLoadingDataset || isUpdatingMembershipRole}
                className={styles.teamListTable}
                columns={columns}
                dataSource={datasetUsers}
                rowKey={({ user }) => user.id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
