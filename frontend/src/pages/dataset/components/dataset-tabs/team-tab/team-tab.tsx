import { Button, Flex, Input } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { UserPopup } from '@/components/modal/user-popup/user-popup';
import { useModal } from '@/hooks/use-modal';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    type OutputPortRoleAssignmentResponse,
    useCreateOutputPortRoleAssignmentMutation,
    useListOutputPortRoleAssignmentsQuery,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import type { UsersGet } from '@/store/api/services/generated/usersApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { Scope } from '@/types/roles';
import { TeamTable } from './components/team-table/team-table.component.tsx';
import styles from './team-tab.module.scss';

function filterUsers(
    assignments: OutputPortRoleAssignmentResponse[],
    searchTerm: string,
): OutputPortRoleAssignmentResponse[] {
    if (!searchTerm) return assignments;

    const searchString = searchTerm.toLowerCase();
    return (
        assignments.filter((assignment) => {
            const user = assignment?.user;
            return (
                user?.email?.toLowerCase()?.includes(searchString) ||
                user?.first_name?.toLowerCase()?.includes(searchString) ||
                user?.last_name?.toLowerCase()?.includes(searchString)
            );
        }) ?? []
    );
}

type Props = {
    datasetId: string;
    dataProductId: string;
};

export function TeamTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { data: dataset } = useGetOutputPortQuery({ id: datasetId, dataProductId });
    const { data: roleAssignments, isFetching } = useListOutputPortRoleAssignmentsQuery({
        outputPortId: datasetId,
    });
    const [addUserToDataset, { isLoading: isAddingUser }] = useCreateOutputPortRoleAssignmentMutation();

    const { data: { roles: DATASET_ROLES = [] } = {}, isFetching: isLoadingRoles } = useGetRolesQuery(Scope.DATASET);
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredUsers = useMemo(() => {
        return filterUsers(roleAssignments?.role_assignments ?? [], searchTerm);
    }, [searchTerm, roleAssignments]);
    const datasetUserIds = useMemo(() => filteredUsers.map((user) => user.user.id), [filteredUsers]);

    const { data: access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__CREATE_USER,
        },
        { skip: !datasetId },
    );
    const canAddUser = access?.allowed || false;

    const handleGrantAccessToDataset = useCallback(
        async (user: UsersGet, role_id: string) => {
            try {
                await addUserToDataset({
                    output_port_id: datasetId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the Output Port'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant access to the Output Port'), type: 'error' });
            }
        },
        [addUserToDataset, datasetId, t],
    );

    if (!dataset || !user) return null;

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
                <TeamTable datasetId={datasetId} datasetUsers={filteredUsers} dataProductId={dataProductId} />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser || isLoadingRoles}
                    userIdsToHide={datasetUserIds}
                    roles={DATASET_ROLES}
                    item={{
                        action: handleGrantAccessToDataset,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
