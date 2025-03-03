import { Button, Popconfirm, TableColumnsType } from 'antd';
import { TFunction } from 'i18next';

import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { UserContract } from '@/types/users';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    onRemoveUserAccess: (userId: string) => void;
    isRemovingUser: boolean;
    canPerformTeamActions: (userId: string) => boolean;
};

export const getDatasetTeamColumns = ({
    t,
    onRemoveUserAccess,
    isRemovingUser,
    canPerformTeamActions,
}: Props): TableColumnsType<UserContract> => {
    const sorter = new Sorter<UserContract>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'first_name',
            render: (_, user) => {
                return <UserAvatar name={`${user.first_name} ${user.last_name}`} email={user.email} />;
            },
            width: '70%',
            sorter: sorter.stringSorter((user) => user.last_name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, user) => (
                <Popconfirm
                    title={t('Remove User')}
                    description={t('Are you sure you want to remove {{name}} from the data product?', {
                        name: user.first_name,
                    })}
                    onConfirm={() => onRemoveUserAccess(user.id)}
                    placement={'leftTop'}
                    okText={t('Confirm')}
                    cancelText={t('Cancel')}
                    okButtonProps={{ loading: isRemovingUser }}
                    autoAdjustOverflow={true}
                >
                    <Button
                        loading={isRemovingUser}
                        disabled={isRemovingUser || !canPerformTeamActions(user.id)}
                        type={'link'}
                    >
                        {t('Remove')}
                    </Button>
                </Popconfirm>
            ),
        },
    ];
};
