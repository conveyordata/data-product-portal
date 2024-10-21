import styles from './environment-config-create.module.scss';
import { Typography, Flex, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { EnvironmentConfigCreateForm } from '@/components/environment-config-create/components/environment-config-create-form.component';

export function EnvironmentConfigCreate() {
    const { t } = useTranslation();
    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('New Environment Configuration')}</Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <EnvironmentConfigCreateForm />
            </Space>
        </Flex>
    );
}
