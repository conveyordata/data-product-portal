import { ProductOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';
import { TechnicalAssetForm } from '@/components/data-products/technical-asset-form/technical-asset-form.component';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { ApplicationPaths, createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation.ts';

type Props = {
    debounce?: number;
};

export function TechnicalAssetCreate({ debounce }: Props) {
    const { dataProductId = '' } = useParams();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { data: dataProduct } = useGetDataProductQuery(dataProductId, { skip: !dataProductId });
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
            { title: dataProduct?.name, path: createDataProductIdPath(dataProductId, TabKeys.OutputPorts) },
            { title: t('New Technical Asset') },
        ]);
    }, [setBreadcrumbs, dataProductId, dataProduct?.name, t]);

    return (
        <TechnicalAssetForm
            mode="create"
            dataProductId={dataProductId}
            debounce={debounce}
            onCreated={(id) => navigate(createDataOutputIdPath(id, dataProductId))}
            onCancel={() => navigate(createDataProductIdPath(dataProductId, TabKeys.OutputPorts))}
        />
    );
}
