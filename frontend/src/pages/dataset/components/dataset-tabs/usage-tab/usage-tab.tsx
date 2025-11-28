import {
    useGetDatasetQueryCuratedQueriesQuery,
    useGetDatasetQueryStatsDailyQuery,
} from '@/store/features/datasets/datasets-api-slice';
import { UsageChart } from './usage-chart';

type Props = {
    datasetId: string;
};

export function UsageTab({ datasetId }: Props) {
    const { data: usageData, isLoading: isUsageLoading } = useGetDatasetQueryStatsDailyQuery(datasetId, {
        skip: !datasetId,
    });

    const { data: curatedQueries, isLoading: areCuratedQueriesLoading } = useGetDatasetQueryCuratedQueriesQuery(
        datasetId,
        {
            skip: !datasetId,
        },
    );

    return (
        <UsageChart
            usageData={usageData}
            curatedQueries={curatedQueries}
            isUsageLoading={isUsageLoading}
            areCuratedQueriesLoading={areCuratedQueriesLoading}
        />
    );
}
