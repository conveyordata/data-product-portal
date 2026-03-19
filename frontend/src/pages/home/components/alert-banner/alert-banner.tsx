import { ArrowRightOutlined, BellOutlined } from '@ant-design/icons';
import { Alert, Button, Typography } from 'antd';
import { useCallback } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { TabKeys } from '@/pages/product-studio/product-studio-tabkeys.ts';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './alert-banner.module.scss';

const { Link } = Typography;

export default function AlertBanner() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: { pending_actions: pendingActions = [] } = {}, isFetching } = useGetUserPendingActionsQuery();
    const actionsCount = pendingActions.length;

    const navigateToRequests = useCallback(() => {
        navigate({
            pathname: ApplicationPaths.Studio,
            hash: TabKeys.Requests,
        });
    }, [navigate]);

    if (isFetching || actionsCount === 0) {
        return null;
    }

    return (
        <Alert
            type="warning"
            showIcon
            icon={<BellOutlined />}
            classNames={{
                root: styles.alertRoot,
                icon: styles.alertIcon,
                title: styles.alertText,
            }}
            title={
                <Trans t={t} count={actionsCount}>
                    You have{' '}
                    <Link strong style={{ color: 'inherit' }} onClick={navigateToRequests}>
                        {/* @ts-expect-error TS2353 */}
                        {{ actionsCount }} pending requests
                    </Link>{' '}
                    waiting for you in the Product Studio
                </Trans>
            }
            action={
                <Button
                    type="link"
                    className={styles.alertText}
                    icon={<ArrowRightOutlined />}
                    iconPlacement="end"
                    onClick={navigateToRequests}
                >
                    {t('View requests')}
                </Button>
            }
        />
    );
}
