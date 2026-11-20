import { Button } from 'antd';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal';
import { DataProductRoleModal } from '@/pages/data-product/components/data-product-role-modal/data-product-role-modal.tsx';
import type { User } from '@/store/api/services/generated/usersApi.ts';
import styles from './data-product-request-access-button.module.scss';

type Props = {
    dataProductId: string;
    user: User;
};

export const DataProductRequestAccessButton = ({ dataProductId, user }: Props) => {
    const { isVisible, handleOpen, handleClose } = useModal();
    const { t } = useTranslation();
    return (
        <>
            <Button type="primary" className={styles.largeButton} onClick={handleOpen}>
                {t('Join Team')}
            </Button>
            {isVisible && (
                <DataProductRoleModal
                    dataProductId={dataProductId}
                    mode="request"
                    initialIdentity={{ ...user, type: 'user' }}
                    onClose={handleClose}
                />
            )}
        </>
    );
};
