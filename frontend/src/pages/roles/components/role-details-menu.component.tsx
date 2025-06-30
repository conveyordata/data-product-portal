import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { Button, Flex } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DeleteRoleModal } from '@/pages/roles/components/delete-role-modal.component.tsx';
import { ModifyRoleModal } from '@/pages/roles/components/modify-role-modal.component.tsx';
import type { RoleContract } from '@/types/roles';
import { Prototype } from '@/types/roles';

type Props = {
    role: RoleContract;
};
export function RoleDetailsMenu({ role }: Props) {
    const { t } = useTranslation();
    const [modifyModalOpen, setModifyModalOpen] = useState(false);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);

    const disabled = role.prototype !== Prototype.CUSTOM;

    return (
        <>
            <Flex vertical align={'flex-start'}>
                <Button type={'text'} icon={<EditOutlined />} onClick={() => setModifyModalOpen(true)}>
                    {t('Modify')}
                </Button>
                <Button
                    type={'text'}
                    icon={<DeleteOutlined />}
                    onClick={() => setDeleteModalOpen(true)}
                    disabled={disabled}
                    danger
                >
                    {t('Delete')}
                </Button>
            </Flex>

            <ModifyRoleModal role={role} isOpen={modifyModalOpen} onClose={() => setModifyModalOpen(false)} />
            <DeleteRoleModal role={role} isOpen={deleteModalOpen} onClose={() => setDeleteModalOpen(false)} />
        </>
    );
}
