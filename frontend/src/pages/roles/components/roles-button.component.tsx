import styles from '@/pages/roles/components/roles-table.module.scss';
import { Button } from 'antd';
import { useTranslation } from 'react-i18next';
import type { RoleScope } from '@/pages/roles/roles.page.tsx';
import { useMemo } from 'react';

type RolesButtonProps = {
    scope: RoleScope;
};
export function RolesButton({ scope }: RolesButtonProps) {
    const { t } = useTranslation();

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
        <Button className={styles.formButton} type={'primary'}>
            {message}
        </Button>
    );
}
