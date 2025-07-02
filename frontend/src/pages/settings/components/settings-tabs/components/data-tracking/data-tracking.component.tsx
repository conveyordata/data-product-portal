
import { Switch, Flex, Space, Typography } from 'antd';
import posthog from '@/config/posthog-config.ts';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

import styles from './data-tracking.module.scss';

export function DataTracking() {
    const { t } = useTranslation();
    const [trackingEnabled, setTrackingEnabled] = useState(() => {
        const saved = sessionStorage.getItem('tracking-enabled');
        return saved === 'true' || saved === null; // default to true
    });

    const handleToggle = (checked: boolean) => {
        setTrackingEnabled(checked);
        sessionStorage.setItem('tracking-enabled', checked.toString());

        if (checked) {
            dispatchMessage({content: t('Data tracking has been enabled'), type: 'success'});
            posthog.opt_in_capturing();
        }
        else {
            posthog.opt_out_capturing();
            dispatchMessage({content: t('Data tracking has been disabled'), type: 'success'});
        }
    };

    return (
        <Flex vertical className={styles.container}>
            <Flex className={styles.globalSettingsHeader}>
                <Typography.Title level={3}>{t('Data Tracking')}</Typography.Title>
            </Flex>
            <Space>
                <Typography.Text>{t('Allow data to be sent to Posthog')}</Typography.Text>
                <Switch defaultChecked={trackingEnabled} onClick={handleToggle}/>
            </Space>
        </Flex>
    );
}