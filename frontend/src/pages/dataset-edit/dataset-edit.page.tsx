import { Typography } from 'antd';
import { useNavigate, useParams } from 'react-router';

import { DatasetForm } from '@/components/datasets/dataset-form/dataset-form.component';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
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
        <>
            <Typography.Title level={3}>{data?.name}</Typography.Title>
            <DatasetForm mode={'edit'} datasetId={datasetId} />
        </>
    );
}
