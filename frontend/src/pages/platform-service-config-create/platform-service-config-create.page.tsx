import styles from './platform-service-config-create.module.scss';
import { Typography, Flex, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { PlatformServiceConfigCreateForm } from '@/components/platform-service-config/components/platform-service-config-create-form.component';

export function PlatformServiceConfigCreate() {
    const { t } = useTranslation();
    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('New Platform Service Configuration')}</Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <PlatformServiceConfigCreateForm />
            </Space>
        </Flex>
    );
}
