import { Flex, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { EnvironmentCreateForm } from '@/components/environment/components/environment-create-form.component';

import styles from './environment-create.module.scss';

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
