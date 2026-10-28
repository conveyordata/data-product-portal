import { Modal, Select } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (userId: string) => void;
};

export function SwitchUserModal({ isOpen, onClose, onSelect }: Props) {
    const { t } = useTranslation();
    const { data: { users = [] } = {} } = useGetUsersQuery(undefined, {
        skip: !isOpen,
    });
    const [selectedUser, setSelectedUser] = useState<string | undefined>(
        localStorage.getItem('activeUserHeader') ?? undefined,
    );
    const userOptions = useMemo(
        () =>
            users.map((user) => ({
                value: user.external_id,
                label: `${user.first_name} ${user.last_name} (${user.email})`,
            })),
        [users],
    );

    return (
        <Modal title={t('Switch user')} open={isOpen} onCancel={onClose} footer={null} centered>
            <Select
                showSearch
                value={selectedUser}
                placeholder={t('Select a user')}
                options={userOptions}
                filterOption={(input, option) => `${option?.label ?? ''}`.toLowerCase().includes(input.toLowerCase())}
                onChange={(value) => {
                    setSelectedUser(value);
                    localStorage.setItem('activeUserHeader', value);
                    window.dispatchEvent(new Event('storage'));
                    window.location.reload();
                    onSelect(value);
                }}
                style={{ width: '100%' }}
            />
        </Modal>
    );
}
