import { Button } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CreateRoleModal } from '@/pages/roles/components/create-role-modal.component';
import styles from '@/pages/roles/components/roles-table.module.scss';
import { Scope } from '@/types/roles';

type RolesButtonProps = {
    scope: Scope;
};
export function CreateRoleButton({ scope }: RolesButtonProps) {
    const { t } = useTranslation();
    const [modalOpen, setModalOpen] = useState(false);

    const message = useMemo(() => {
        switch (scope) {
            case Scope.GLOBAL:
                return t('Create new global role');
            case Scope.DATA_PRODUCT:
                return t('Create new data product role');
            case Scope.DATASET:
                return t('Create new dataset role');
            default:
                throw new Error('Invalid scope');
        }
    }, [scope, t]);

    return (
        <>
            <Button
                className={styles.formButton}
                type={'primary'}
                onClick={() => {
                    setModalOpen(true);
                }}
            >
                {message}
            </Button>

            <CreateRoleModal scope={scope} title={message} isOpen={modalOpen} onClose={() => setModalOpen(false)} />
        </>
    );
}
