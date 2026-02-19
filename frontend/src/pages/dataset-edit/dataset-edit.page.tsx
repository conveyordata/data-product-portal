import { Typography } from 'antd';
import { useNavigate, useParams } from 'react-router';

import { DatasetForm } from '@/components/datasets/dataset-form/dataset-form.component';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

export function DatasetEdit() {
    const { datasetId = '', dataProductId = '' } = useParams();
    const { data, isError } = useGetOutputPortQuery(
        { id: datasetId, dataProductId },
        { skip: !datasetId || !dataProductId },
    );
    const navigate = useNavigate();

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
