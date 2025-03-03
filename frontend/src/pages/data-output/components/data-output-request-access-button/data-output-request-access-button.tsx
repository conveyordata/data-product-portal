import { Button } from 'antd';
import { useTranslation } from 'react-i18next';

import { useRequestMembershipAccessMutation } from '@/store/features/data-output-memberships/data-output-memberships-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

import styles from './data-output-request-access-button.module.scss';

type Props = {
    dataOutputId: string;
    userId: string;
};

export const DataOutputRequestAccessButton = ({ dataOutputId, userId }: Props) => {
    const { t } = useTranslation();
    const [userRequestDataOutputAcces, { isLoading }] = useRequestMembershipAccessMutation();

    const handleRequestAccess = async () => {
        try {
            await userRequestDataOutputAcces({ dataOutputId, userId }).unwrap();
            dispatchMessage({ content: t('Request sent successfully'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to request access to data output'), type: 'error' });
        }
    };

    return (
        <Button type="primary" className={styles.largeButton} onClick={handleRequestAccess} loading={isLoading}>
            {t('Join Team')}
        </Button>
    );
};
