import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { DatasetCuratedQueriesContract } from '@/types/dataset';
import type {
    DatasetQueryStatsDailyResponses,
    DatasetQueryStatsGranularity,
} from '@/types/dataset/dataset-query-stats-daily.contract.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract.ts';
import type { DatasetsSearchContract } from '@/types/dataset/datasets-search.contract.ts';
import type { QueryParams } from '@/types/http.ts';

export const datasetTags: string[] = [TagTypes.Dataset, TagTypes.UserDatasets, TagTypes.DataProduct, TagTypes.History];

export const datasetsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: datasetTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllDatasets: builder.query<DatasetsGetContract, void>({
            query: () => ({
                url: ApiUrl.Datasets,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.Dataset as const, id })),
                      ]
                    : [{ type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST }],
        }),
        searchDatasets: builder.query<DatasetsSearchContract, { query: string }>({
            query: (query) => ({
                url: ApiUrl.DatasetSearch,
                params: query,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.Dataset as const, id })),
                      ]
                    : [{ type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST }],
        }),
        getDatasetQueryCuratedQueries: builder.query<DatasetCuratedQueriesContract, string>({
            query: (datasetId) => ({
                url: buildUrl(ApiUrl.DatasetCuratedQueries, { datasetId }),
                method: 'GET',
            }),
            providesTags: (_, __, datasetId) => [{ type: TagTypes.Dataset as const, id: datasetId }],
        }),
        getUserDatasets: builder.query<DatasetsGetContract, string>({
            query: (userId) => ({
                url: buildUrl(ApiUrl.UserDatasets, { userId }),
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST }],
        }),
        getDatasetQueryStatsDaily: builder.query<
            DatasetQueryStatsDailyResponses,
            {
                datasetId: string;
                granularity?: DatasetQueryStatsGranularity;
                dayRange?: number;
            }
        >({
            query: ({ datasetId, granularity, dayRange }) => {
                const params: QueryParams = {};

                if (granularity) {
                    params.granularity = granularity;
                }

                if (typeof dayRange === 'number') {
                    params.day_range = dayRange;
                }

                return {
                    url: buildUrl(ApiUrl.DatasetQueryStats, { datasetId }),
                    method: 'GET',
                    params,
                };
            },
        }),
    }),
    overrideExisting: false,
});

export const {
    useSearchDatasetsQuery,
    useGetAllDatasetsQuery,
    useGetDatasetQueryCuratedQueriesQuery,
    useGetUserDatasetsQuery,
    useGetDatasetQueryStatsDailyQuery,
} = datasetsApiSlice;
