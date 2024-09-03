import { Flex, Table, TableColumnsType } from 'antd';
import { UserContract } from '@/types/users';
import { useMemo } from 'react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import styles from './team-table.module.scss';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
// import { DataOutputMembershipRole, DataOutputUserMembership } from '@/types/data-output-membership';
import { getDataOutputUsersTableColumns } from '@/pages/data-output/components/data-output-tabs/team-tab/components/team-table/team-table-columns.tsx';
// import {
//     useDenyMembershipAccessMutation,
//     useGrantMembershipAccessMutation,
//     useRemoveMembershipAccessMutation,
//     useUpdateMembershipRoleMutation,
// } from '@/store/features/data-output-memberships/data-output-memberships-api-slice.ts';
// import { getDoesUserHaveAnyDataOutputMembership } from '@/utils/data-output-user-role.helper.ts';

type Props = {
    isCurrentUserDataOutputOwner: boolean;
    dataOutputId: string;
    dataOutputUsers: DataOutputUserMembership[];
};

function canPerformTeamActions(isCurrentUserDataOutputOwner: boolean, userId: string, currentUserId: string) {
    return isCurrentUserDataOutputOwner && userId !== currentUserId;
}

export function TeamTable({ isCurrentUserDataOutputOwner, dataOutputId, dataOutputUsers }: Props) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser) as UserContract;
    const { data: dataOutput, isLoading: isLoadingDataOutput } = useGetDataOutputByIdQuery(dataOutputId);
    const [updateMembershipRole, { isLoading: isUpdatingMembershipRole }] = useUpdateMembershipRoleMutation();
    const [removeUserFromDataOutput, { isLoading: isRemovingUserFromDataOutput }] =
        useRemoveMembershipAccessMutation();
    const [grantMembershipAccess] = useGrantMembershipAccessMutation();
    const [denyMembershipAccess] = useDenyMembershipAccessMutation();

    const handleRemoveUserAccess = async (membershipId: string) => {
        try {
            if (!dataOutput) return;

            await removeUserFromDataOutput({ membershipId }).unwrap();
            dispatchMessage({ content: t('User access to data output has been removed'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Failed to remove user access'), type: 'error' });
        }
    };

    const handleGrantAccessToDataOutput = async (membershipId: string) => {
        try {
            await grantMembershipAccess({ membershipId }).unwrap();
            dispatchMessage({ content: t('User has been granted access to the data output'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Failed to grant user access to the data output'), type: 'error' });
        }
    };

    const handleDenyAccessToDataOutput = async (membershipId: string) => {
        try {
            await denyMembershipAccess({ membershipId }).unwrap();
            dispatchMessage({ content: t('User access to the data output has been denied'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Failed to deny user access to the data output'), type: 'error' });
        }
    };

    const handleRoleChange = async (role: DataOutputMembershipRole, membershipId: string) => {
        if (!dataOutput) return;
        try {
            await updateMembershipRole({ dataOutputId: dataOutput.id, membershipId, role }).unwrap();
            dispatchMessage({ content: t('User role has been updated'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Failed to update user role'), type: 'error' });
        }
    };

    const columns: TableColumnsType<DataOutputUserMembership> = useMemo(() => {
        return getDataOutputUsersTableColumns({
            t,
            onRemoveMembership: handleRemoveUserAccess,
            onRoleChange: handleRoleChange,
            isRemovingUser: isRemovingUserFromDataOutput,
            dataOutputUsers: dataOutputUsers,
            canPerformTeamActions: (userId: string) =>
                canPerformTeamActions(isCurrentUserDataOutputOwner, userId, currentUser.id),
            isLoading: isLoadingDataOutput || isUpdatingMembershipRole,
            hasCurrentUserMembership: getDoesUserHaveAnyDataOutputMembership(currentUser.id, dataOutputUsers),
            onRejectMembershipRequest: handleDenyAccessToDataOutput,
            onAcceptMembershipRequest: handleGrantAccessToDataOutput,
        });
    }, [t, isCurrentUserDataOutputOwner, currentUser.id, dataOutputUsers]);

    if (!dataOutput) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<DataOutputUserMembership>
                loading={isLoadingDataOutput || isUpdatingMembershipRole}
                className={styles.teamListTable}
                columns={columns}
                dataSource={dataOutputUsers}
                rowKey={({ user }) => user.id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
