import { Button } from 'antd';
import { useTranslation } from 'react-i18next';

import { useRequestMembershipAccessMutation } from '@/store/features/data-product-memberships/data-product-memberships-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

import styles from './data-product-request-access-button.module.scss';

type Props = {
    dataProductId: string;
    userId: string;
};

export const DataProductRequestAccessButton = ({ dataProductId, userId }: Props) => {
    const { t } = useTranslation();
    const [userRequestDataProductAcces, { isLoading }] = useRequestMembershipAccessMutation();

    const handleRequestAccess = async () => {
        try {
            await userRequestDataProductAcces({ dataProductId, userId }).unwrap();
            dispatchMessage({ content: t('Request sent successfully'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to request access to data product'), type: 'error' });
        }
    };

    return (
        <Button type="primary" className={styles.largeButton} onClick={handleRequestAccess} loading={isLoading}>
            {t('Join Team')}
        </Button>
    );
};
