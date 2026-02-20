import { ProductOutlined, ShopOutlined } from '@ant-design/icons';
import { Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, useParams } from 'react-router';
import { DatasetForm } from '@/components/datasets/dataset-form/dataset-form.component';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    ApplicationPaths,
    createDataProductIdPath,
    createMarketplaceOutputPortPath,
    createOutputPortPath,
} from '@/types/navigation.ts';

export function DatasetEdit() {
    const { t } = useTranslation();
    const { datasetId = '', dataProductId = '' } = useParams();
    const { data, isError } = useGetOutputPortQuery(
        { id: datasetId, dataProductId },
        { skip: !datasetId || !dataProductId },
    );
    const navigate = useNavigate();

    const { pathname } = useLocation();
    const { setBreadcrumbs } = useBreadcrumbs();
    const { data: outputPort } = useGetOutputPortQuery(
        { dataProductId, id: datasetId },
        { skip: !dataProductId || !datasetId },
    );
    const { data: data_product } = useGetDataProductQuery(dataProductId, {
        skip: !dataProductId,
    });
    useEffect(() => {
        if (pathname.includes('studio')) {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            <ProductOutlined /> {t('Product Studio')}
                        </>
                    ),
                    path: ApplicationPaths.Studio,
                },
                { title: <>{data_product?.name}</>, path: createDataProductIdPath(dataProductId) },
                { title: <>{outputPort?.name}</>, path: createOutputPortPath(dataProductId, datasetId) },
                { title: <>{t('Edit')}</> },
            ]);
        } else {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            {' '}
                            <ShopOutlined /> {t('Marketplace')}
                        </>
                    ),
                    path: ApplicationPaths.Marketplace,
                },
                { title: <>{data_product?.name}</>, path: createDataProductIdPath(dataProductId) },
                { title: <>{outputPort?.name}</>, path: createMarketplaceOutputPortPath(dataProductId, datasetId) },
                { title: <>{t('Edit')}</> },
            ]);
        }
    }, [setBreadcrumbs, data_product, outputPort, dataProductId, datasetId, pathname, t]);

    if (!datasetId || isError) {
        navigate(ApplicationPaths.Marketplace, { replace: true });
        return null;
    }

    return (
        <>
            <Typography.Title level={3}>{data?.name}</Typography.Title>
            <DatasetForm mode={'edit'} datasetId={datasetId} dataProductId={dataProductId} />
        </>
    );
}
