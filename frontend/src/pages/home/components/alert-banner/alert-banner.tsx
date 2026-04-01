import { ArrowRightOutlined, BellOutlined } from '@ant-design/icons';
import { Alert, Button, ConfigProvider, Typography, theme } from 'antd';
import { useCallback } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { TabKeys } from '@/pages/product-studio/product-studio-tabkeys.ts';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './alert-banner.module.scss';

const { Text } = Typography;

export function AlertBanner() {
    const { t } = useTranslation();
    const { token } = theme.useToken();
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
        <ConfigProvider
            theme={{
                token: { colorText: token.colorInfoText },
            }}
        >
            <Alert
                type="info"
                showIcon
                icon={<BellOutlined />}
                onClick={navigateToRequests}
                classNames={{ root: styles.alertRoot }}
                title={
                    <Trans t={t} values={{ count: actionsCount }}>
                        You have{' '}
                        <Text strong style={{ color: 'inherit' }}>
                            {'{{ count }}'} pending requests
                        </Text>{' '}
                        waiting for you in the Product Studio
                    </Trans>
                }
                action={
                    <Button type="link" icon={<ArrowRightOutlined />} iconPlacement="end">
                        {t('View requests')}
                    </Button>
                }
            />
        </ConfigProvider>
    );
}
