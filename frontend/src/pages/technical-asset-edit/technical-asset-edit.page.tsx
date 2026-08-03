import { ProductOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { TechnicalAssetForm } from '@/pages/technical-asset-edit/technical-asset-form/technical-asset-form.component';
import { useGetTechnicalAssetQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { ApplicationPaths, createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation.ts';
import styles from './technical-asset-edit.module.scss';

export function TechnicalAssetEdit() {
    const { dataOutputId, dataProductId } = useParams();
    const { t } = useTranslation();
    const { data: dataOutput, isError } = useGetTechnicalAssetQuery(
        {
            id: dataOutputId || '',
            dataProductId: dataProductId || '',
        },
        { skip: !dataOutputId || !dataProductId },
    );
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
            { title: <>{dataOutput?.owner.name}</>, path: createDataProductIdPath(dataProductId ?? '') },
            { title: <>{dataOutput?.name}</>, path: createDataOutputIdPath(dataOutputId ?? '', dataProductId ?? '') },
            { title: t('Edit') },
        ]);
    }, [setBreadcrumbs, dataOutputId, dataOutput, dataProductId, t]);
    const navigate = useNavigate();

    if (!dataOutputId || !dataProductId || isError) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3} className={styles.title}>
                {dataOutput?.name}
            </Typography.Title>
            <Space orientation="vertical" size="large" className={styles.container}>
                <TechnicalAssetForm dataOutputId={dataOutputId} dataProductId={dataProductId} mode="edit" />
            </Space>
        </Flex>
    );
}
