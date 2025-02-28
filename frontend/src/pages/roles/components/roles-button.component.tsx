import { Button } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import styles from '@/pages/roles/components/roles-table.module.scss';
import type { RoleScope } from '@/pages/roles/roles.page';
import { CreateRoleModal } from '@/pages/roles/components/create-role-modal.component';

type RolesButtonProps = {
    scope: RoleScope;
};
export function CreateRoleButton({ scope }: RolesButtonProps) {
    const { t } = useTranslation();
    const [modalOpen, setModalOpen] = useState(false);

    const message = useMemo(() => {
        switch (scope) {
            case 'global':
                return t('Create new global role');
            case 'data_product':
                return t('Create new data product role');
            case 'dataset':
                return t('Create new dataset role');
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
