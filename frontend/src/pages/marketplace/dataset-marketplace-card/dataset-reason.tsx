import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useGetDatasetReasoningForQueryQuery } from '@/store/features/datasets/datasets-api-slice.ts';

type Props = {
    dataset_id: string;
    query: string;
};

export function DatasetReason({ dataset_id, query }: Props) {
    const { data, isFetching } = useGetDatasetReasoningForQueryQuery({
        datasetId: dataset_id,
        query,
    });
    return isFetching || !data ? <LoadingSpinner /> : <div style={{ width: '300px' }}>{data.reason}</div>;
}
