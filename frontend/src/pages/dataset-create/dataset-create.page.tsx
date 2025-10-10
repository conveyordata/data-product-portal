import { Flex, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router';

import { DatasetForm } from '@/components/datasets/dataset-form/dataset-form.component';

import styles from './dataset-create.module.scss';

export function DatasetCreate() {
    const { t } = useTranslation();
    const [searchParams] = useSearchParams();
    const dataProductId = searchParams.get('dataProductId');
    const dataOutputId = searchParams.get('dataOutputId');

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('New Dataset')}</Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <DatasetForm
                    mode={'create'}
                    dataProductId={dataProductId ?? undefined}
                    dataOutputId={dataOutputId ?? undefined}
                />
            </Space>
        </Flex>
    );
}
