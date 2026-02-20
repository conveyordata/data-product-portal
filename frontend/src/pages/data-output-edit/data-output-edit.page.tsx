import { ProductOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';
import { DataOutputForm } from '@/components/data-outputs/data-output-form/data-output-form.component';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useGetTechnicalAssetQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { ApplicationPaths, createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation.ts';
import styles from './data-output-edit.module.scss';

export function DataOutputEdit() {
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
                <DataOutputForm dataOutputId={dataOutputId} dataProductId={dataProductId} mode="edit" />
            </Space>
        </Flex>
    );
}
