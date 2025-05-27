import { Button, Flex, Form } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Searchbar } from '@/components/form';
import { UserPopup } from '@/components/modal/user-popup/user-popup';
import { useModal } from '@/hooks/use-modal';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useCreateDatasetRoleAssignmentMutation,
    useGetDatasetRoleAssignmentsQuery,
} from '@/store/features/role-assignments/dataset-roles-api-slice';
import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DatasetRoleAssignmentContract } from '@/types/roles/role.contract';
import type { SearchForm } from '@/types/shared';
import type { UserContract } from '@/types/users';

import { TeamTable } from './components/team-table/team-table.component.tsx';
import styles from './team-tab.module.scss';

function filterUsers(
    assignments: DatasetRoleAssignmentContract[],
    searchTerm: string,
): DatasetRoleAssignmentContract[] {
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
};

export function TeamTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { data: dataset } = useGetDatasetByIdQuery(datasetId);
    const { data: roleAssignments, isFetching } = useGetDatasetRoleAssignmentsQuery({
        dataset_id: datasetId,
    });
    const [addUserToDataset, { isLoading: isAddingUser }] = useCreateDatasetRoleAssignmentMutation();

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const { data: DATASET_ROLES, isFetching: isLoadingRoles } = useGetRolesQuery('dataset');

    const filteredUsers = useMemo(() => {
        return filterUsers(roleAssignments ?? [], searchTerm);
    }, [searchTerm, roleAssignments]);
    const datasetUserIds = useMemo(() => filteredUsers.map((user) => user.user.id), [filteredUsers]);

    const { data: access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__CREATE_USER,
        },
        { skip: !datasetId },
    );
    const canAddUser = access?.allowed || false;

    const handleGrantAccessToDataset = useCallback(
        async (user: UserContract, role_id: string) => {
            try {
                await addUserToDataset({
                    dataset_id: datasetId,
                    user_id: user.id,
                    role_id: role_id,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the dataset'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant access to the dataset'), type: 'error' });
            }
        },
        [addUserToDataset, datasetId, t],
    );

    if (!dataset || !user) return null;

    return (
        <>
            <Flex vertical className={`${styles.container} ${filteredUsers.length === 0 && styles.paginationGap}`}>
                <Searchbar
                    form={searchForm}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    placeholder={t('Search users by email or name')}
                    actionButton={
                        <Button
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                            disabled={!canAddUser}
                        >
                            {t('Add User')}
                        </Button>
                    }
                />
                <TeamTable datasetId={datasetId} datasetUsers={filteredUsers} />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser || isLoadingRoles}
                    userIdsToHide={datasetUserIds}
                    roles={DATASET_ROLES || []}
                    item={{
                        action: handleGrantAccessToDataset,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
