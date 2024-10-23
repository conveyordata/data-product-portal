import styles from './environment-create.module.scss';
import { Typography, Flex, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { EnvironmentCreateForm } from '@/components/environment/components/environment-create-form.component';

export function EnvironmentCreate() {
    const { t } = useTranslation();
    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('New Environment')}</Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <EnvironmentCreateForm />
            </Space>
        </Flex>
    );
}
