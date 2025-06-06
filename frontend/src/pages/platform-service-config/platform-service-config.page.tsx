import { Button, Flex, Input, Space, Typography } from 'antd';
import { type ChangeEvent, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetPlatformServiceConfigByIdQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import type { DynamicPathParams } from '@/types/navigation';

import styles from './platform-service-config.module.scss';

const { TextArea } = Input;

export function PlatformServiceConfig() {
    const { t } = useTranslation();
    const { platformServiceConfigId = '' } = useParams<DynamicPathParams>();

    const { data: platformServiceConfig, isLoading } = useGetPlatformServiceConfigByIdQuery(platformServiceConfigId, {
        skip: !platformServiceConfigId,
    });

    const [isEdit, setIsEdit] = useState(false);
    // const [configValue, setConfigValue] = useState('');
    const [currentConfigValue, setCurrentConfigValue] = useState('');

    const handleConfigUpdate = () => {
        try {
            const config = JSON.parse(currentConfigValue);
            // setConfigValue(JSON.stringify(config, undefined, 4));
            setCurrentConfigValue(JSON.stringify(config, undefined, 4));
            setIsEdit(false);
            // TODO: Implement config update
            dispatchMessage({ content: t('Platform Service Configuration updated successfully'), type: 'success' });
        } catch (_e) {
            dispatchMessage({ content: t('Invalid config format'), type: 'error' });
        }
    };

    const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setCurrentConfigValue(e.target.value);
    };

    const handleCancel = () => {
        setIsEdit(false);
        // setCurrentConfigValue(configValue);
        setCurrentConfigValue(JSON.stringify(platformServiceConfig?.config, undefined, 4));
    };

    useEffect(() => {
        if (platformServiceConfig) {
            const config = JSON.stringify(platformServiceConfig.config, undefined, 4);
            // setConfigValue(config);
            setCurrentConfigValue(config);
        }
    }, [platformServiceConfig]);

    if (isLoading) return <LoadingSpinner />;

    if (!platformServiceConfig) return null;

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('Platform Service Configuration')}</Typography.Title>
            <div className={styles.textareaContainer}>
                <TextArea
                    autoSize={{ minRows: 5 }}
                    value={currentConfigValue}
                    disabled={!isEdit}
                    onChange={handleChange}
                />
            </div>
            <Space className={styles.buttonsContainer}>
                {isEdit ? (
                    <Button className={styles.formButton} type="primary" onClick={handleConfigUpdate}>
                        {t('Save')}
                    </Button>
                ) : (
                    <Button className={styles.formButton} type="primary" onClick={() => setIsEdit(true)}>
                        {t('Edit')}
                    </Button>
                )}

                <Button className={styles.formButton} type="default" disabled={!isEdit} onClick={handleCancel}>
                    {t('Cancel')}
                </Button>
            </Space>
        </Flex>
    );
}
