import { Flex, Space, Typography } from 'antd';
import styles from './dataset-edit.module.scss';
import { DatasetForm } from '@/components/datasets/components/dataset-form.component.tsx';
import { useNavigate, useParams } from 'react-router-dom';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

export function DatasetEdit() {
    const { datasetId = '' } = useParams();
    const { data, isError } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const navigate = useNavigate();

    if (!datasetId || isError) {
        navigate(ApplicationPaths.Datasets, { replace: true });
        return null;
    }

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{data?.name}</Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <DatasetForm mode={'edit'} datasetId={datasetId} />
            </Space>
        </Flex>
    );
}
