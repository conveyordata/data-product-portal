import { Flex, Space, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';

import { DataOutputForm } from '@/components/data-outputs/data-output-form/data-output-form.component';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { ApplicationPaths } from '@/types/navigation.ts';

import styles from './data-output-edit.module.scss';

export function DataOutputEdit() {
    const { dataOutputId } = useParams();
    const { data: dataOutput, isError } = useGetDataOutputByIdQuery(dataOutputId || '', { skip: !dataOutputId });
    const navigate = useNavigate();

    if (!dataOutputId || isError) {
        navigate(ApplicationPaths.DataProducts, { replace: true });
        return null;
    }

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3} className={styles.title}>
                {dataOutput?.name}
            </Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <DataOutputForm dataOutputId={dataOutputId} mode="edit" />
            </Space>
        </Flex>
    );
}
