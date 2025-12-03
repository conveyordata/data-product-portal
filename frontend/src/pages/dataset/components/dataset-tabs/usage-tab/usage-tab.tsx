import { useGetDatasetQueryStatsDailyQuery } from '@/store/features/datasets/datasets-api-slice';
import { UsageChart } from './usage-chart';

type Props = {
    datasetId: string;
};

export function UsageTab({ datasetId }: Props) {
    const { data, isLoading } = useGetDatasetQueryStatsDailyQuery(datasetId);

    return <UsageChart data={data} isLoading={isLoading} />;
}
