import { Flex, Space, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router';

import { DataOutputForm } from '@/components/data-outputs/data-output-form/data-output-form.component';
import { useGetTechnicalAssetQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './data-output-edit.module.scss';

export function DataOutputEdit() {
    const { dataOutputId, dataProductId } = useParams();
    const { data: dataOutput, isError } = useGetTechnicalAssetQuery(
        {
            id: dataOutputId || '',
            dataProductId: dataProductId || '',
        },
        { skip: !dataOutputId || !dataProductId },
    );
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
