import styles from './team-tab.module.scss';
import { Button, Flex, Form } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCallback, useMemo } from 'react';
import { useModal } from '@/hooks/use-modal.tsx';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
// import { getIsDataOutputOwner } from '@/utils/data-output-user-role.helper.ts';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { TeamTable } from '@/pages/data-output/components/data-output-tabs/team-tab/components/team-table/team-table.component.tsx';
import { SearchForm } from '@/types/shared';
import { Searchbar } from '@/components/form';
// import { DataOutputMembershipRole, DataOutputUserMembership } from '@/types/data-output-membership';
import { UserPopup } from '@/components/modal/user-popup/user-popup.tsx';
import { UserContract } from '@/types/users';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
// import { useAddDataOutputMembershipMutation } from '@/store/features/data-output-memberships/data-output-memberships-api-slice.ts';

type Props = {
    dataOutputId: string;
};

function filterUsers(users: DataOutputUserMembership[], searchTerm: string) {
    if (!searchTerm) return users;
    if (!users) return [];

    return (
        users.filter(
            (membership) =>
                membership?.user?.email?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                membership?.user?.first_name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                membership?.user?.last_name?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function TeamTab({ dataOutputId }: Props) {
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { data: dataOutput, isFetching } = useGetDataOutputByIdQuery(dataOutputId);
    const [addUserToDataOutput, { isLoading: isAddingUser }] = useAddDataOutputMembershipMutation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredUsers = useMemo(() => {
        return filterUsers(dataOutput?.memberships ?? [], searchTerm);
    }, [dataOutput?.memberships, searchTerm]);
    const dataOutputUserIds = useMemo(() => filteredUsers.map((user) => user.user.id), [filteredUsers]);

    const isDataOutputOwner = useMemo(() => {
        if (!dataOutput || !user) return false;

        return getIsDataOutputOwner(dataOutput, user.id) || user.is_admin;
    }, [dataOutput?.id, user?.id]);

    const handleGrantAccessToDataOutput = useCallback(
        async (user: UserContract) => {
            try {
                await addUserToDataOutput({
                    dataOutputId: dataOutputId,
                    user_id: user.id,
                    role: DataOutputMembershipRole.Member,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data output'), type: 'success' });
            } catch (error) {
                dispatchMessage({ content: t('Failed to grant access to the data output'), type: 'error' });
            }
        },
        [addUserToDataOutput, dataOutputId, t],
    );

    if (!dataOutput || !user) return null;

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    form={searchForm}
                    formItemProps={{ initialValue: '' }}
                    placeholder={t('Search users by email or name')}
                    actionButton={
                        <Button
                            disabled={!isDataOutputOwner}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add User')}
                        </Button>
                    }
                />
                <TeamTable
                    isCurrentUserDataOutputOwner={isDataOutputOwner}
                    dataOutputId={dataOutputId}
                    dataOutputUsers={filteredUsers}
                />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser}
                    userIdsToHide={dataOutputUserIds}
                    item={{
                        action: handleGrantAccessToDataOutput,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
