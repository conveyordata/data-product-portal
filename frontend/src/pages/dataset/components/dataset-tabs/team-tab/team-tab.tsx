import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Searchbar } from '@/components/form';
import { UserPopup } from '@/components/modal/user-popup/user-popup.tsx';
import { useModal } from '@/hooks/use-modal.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useAddUserToDatasetMutation, useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { DatasetMembershipContract } from '@/types/dataset-membership/dataset-membership.contract.ts';
import { SearchForm } from '@/types/shared';
import { UserContract } from '@/types/users';
import { getIsDatasetOwner } from '@/utils/dataset-user.helper.ts';

import { TeamTable } from './components/team-table/team-table.component.tsx';
import styles from './team-tab.module.scss';

type Props = {
    datasetId: string;
};

function filterUsers(users: DatasetMembershipContract[], searchTerm: string) {
    if (!searchTerm) return users;
    if (!users) return [];

    return (
        users.filter(
            (user) =>
                user?.email?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                user?.first_name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                user?.last_name?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function TeamTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { data: dataset, isFetching } = useGetDatasetByIdQuery(datasetId);
    const [addUserToDataset, { isLoading }] = useAddUserToDatasetMutation();

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const datasetOwnerIds = dataset?.owners.map((owner) => owner.id) ?? [];
    const { data: access } = useCheckAccessQuery(
        {
            object_id: datasetId,
            action: AuthorizationAction.DATASET_CREATE_USER,
        },
        { skip: !datasetId },
    );
    const canAddNew = access?.access || false;

    const filteredUsers = useMemo(() => {
        return filterUsers(dataset?.memberships ?? [], searchTerm);
    }, [dataset?.memberships, searchTerm]);

    const isDatasetOwner = useMemo(() => {
        if (!dataset || !user) return false;

        return getIsDatasetOwner(dataset, user.id) || user.is_admin;
    }, [dataset, user]);

    const handleAddNewUser = async (user: UserContract) => {
        try {
            await addUserToDataset({ datasetId, userId: user.id }).unwrap();
            dispatchMessage({ content: t('User has been added to dataset'), type: 'success' });
        } catch (_e) {
            dispatchMessage({ content: t('Failed to add user to dataset'), type: 'error' });
        }
    };

    if (!dataset || !user) return null;

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    form={searchForm}
                    formItemProps={{ initialValue: '' }}
                    placeholder={t('Search users by email or name')}
                    actionButton={
                        <Button
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                            disabled={!(canAddNew || isDatasetOwner)}
                        >
                            {t('Add User')}
                        </Button>
                    }
                />
                <TeamTable
                    isCurrentUserDatasetOwner={isDatasetOwner}
                    datasetUsers={filteredUsers}
                    datasetId={datasetId}
                />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    userIdsToHide={datasetOwnerIds}
                    isLoading={isFetching || isLoading}
                    item={{
                        action: handleAddNewUser,
                        label: t('Add User'),
                    }}
                />
            )}
        </>
    );
}
