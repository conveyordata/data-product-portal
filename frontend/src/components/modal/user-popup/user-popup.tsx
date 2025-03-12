import { Button, Form, List, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { SearchForm } from '@/types/shared';
import { UserContract } from '@/types/users';

import styles from './user-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    isLoading: boolean;
    userIdsToHide?: string[];
    item: {
        action: (user: UserContract) => void;
        label: string;
    };
};

const handleUserListFilter = (users: UserContract[], searchTerm: string) => {
    return users.filter((user) => {
        return (
            user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            `${user.first_name} ${user.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
        );
    });
};

export function UserPopup({ onClose, isOpen, item, isLoading, userIdsToHide }: Props) {
    const { t } = useTranslation();
    const { data: users = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const [searchUsersForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchUsersForm);

    const filteredUsers = useMemo(() => {
        const filteredOutHiddenUsers = users.filter((user) => !userIdsToHide?.includes(user.id));
        return searchTerm ? handleUserListFilter(filteredOutHiddenUsers, searchTerm) : filteredOutHiddenUsers;
    }, [userIdsToHide, users, searchTerm]);

    return (
        <FormModal title={t('Add User')} onClose={onClose} isOpen={isOpen} footer={(_, { CancelBtn }) => <CancelBtn />}>
            <Searchbar
                form={searchUsersForm}
                formItemProps={{ initialValue: '', className: styles.searchFieldWrapper }}
            />
            <div className={styles.userList}>
                <List
                    loading={isLoading || isFetchingUsers}
                    size={'large'}
                    locale={{ emptyText: t('No users found') }}
                    rowKey={(user) => user.id}
                    dataSource={filteredUsers}
                    renderItem={(user) => {
                        return (
                            <List.Item key={user.id}>
                                <List.Item.Meta
                                    title={
                                        <Typography.Text
                                            className={styles.userName}
                                        >{`${user.first_name} ${user.last_name}`}</Typography.Text>
                                    }
                                    description={<Typography.Link>{user.email}</Typography.Link>}
                                />
                                <Button
                                    disabled={isLoading || isFetchingUsers}
                                    loading={isLoading || isFetchingUsers}
                                    type={'link'}
                                    onClick={() => item.action(user)}
                                >
                                    {item.label}
                                </Button>
                            </List.Item>
                        );
                    }}
                />
            </div>
        </FormModal>
    );
}
