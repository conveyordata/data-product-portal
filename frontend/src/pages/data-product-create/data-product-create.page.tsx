import { Flex, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import styles from './data-product-create.module.scss';

export function DataProductCreate() {
    const { t } = useTranslation();

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3} className={styles.title}>
                {t(`New Data Product`)}
            </Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <DataProductForm mode={'create'} />
            </Space>
        </Flex>
    );
}
