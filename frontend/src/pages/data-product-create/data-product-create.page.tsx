import { ProductOutlined } from '@ant-design/icons';
import { Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

export function DataProductCreate() {
    const { t } = useTranslation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined /> {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: t('New Data Product') },
        ]);
    }, [setBreadcrumbs, t]);

    return (
        <>
            <Typography.Title level={3}>{t('New Data Product')}</Typography.Title>
            <DataProductForm mode={'create'} />
        </>
    );
}
