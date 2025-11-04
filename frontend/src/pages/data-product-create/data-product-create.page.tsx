import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';

export function DataProductCreate() {
    const { t } = useTranslation();

    return (
        <>
            <Typography.Title level={3}>{t('New Data Product')}</Typography.Title>
            <DataProductForm mode={'create'} />
        </>
    );
}
