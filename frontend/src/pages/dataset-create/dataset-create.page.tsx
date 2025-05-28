import { Flex, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { DatasetForm } from '@/components/datasets/dataset-form/dataset-form.component';

import styles from './dataset-create.module.scss';

export function DatasetCreate() {
    const { t } = useTranslation();
    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('New Dataset')}</Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <DatasetForm mode={'create'} />
            </Space>
        </Flex>
    );
}
