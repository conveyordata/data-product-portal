import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type {
    DatasetContract,
    DatasetCreateRequest,
    DatasetCreateResponse,
    DatasetUpdateRequest,
    DatasetUpdateResponse,
} from '@/types/dataset';
import type {
    DatasetQueryStatsDailyResponses,
    DatasetQueryStatsGranularity,
} from '@/types/dataset/dataset-query-stats-daily.contract.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract.ts';
import type { DatasetsSearchContract } from '@/types/dataset/datasets-search.contract.ts';
import type { EventContract } from '@/types/events/event.contract';
import type { GraphContract } from '@/types/graph/graph-contract';
import type { QueryParams } from '@/types/http.ts';
import type {
    NamespaceLengthLimitsResponse,
    NamespaceSuggestionResponse,
    NamespaceValidationResponse,
} from '@/types/namespace/namespace';

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
        getUserDatasets: builder.query<DatasetsGetContract, string>({
            query: (userId) => ({
                url: buildUrl(ApiUrl.UserDatasets, { userId }),
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST }],
        }),
        getDatasetById: builder.query<DatasetContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DatasetGet, { datasetId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [
                { type: TagTypes.Dataset as const, id: id },
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        getDatasetHistory: builder.query<EventContract[], string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DatasetHistory, { datasetId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [{ type: TagTypes.History as const, id: id }],
        }),
        createDataset: builder.mutation<DatasetCreateResponse, DatasetCreateRequest>({
            query: ({ data_product_id, ...dataset }) => ({
                url: ApiUrl.Datasets,
                method: 'POST',
                data: { data_product_id, ...dataset },
            }),
            invalidatesTags: (_, __, { data_product_id }) => [
                { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const, id: data_product_id },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        removeDataset: builder.mutation<void, DatasetContract>({
            query: (dataset) => ({
                url: buildUrl(ApiUrl.DatasetGet, { datasetId: dataset.id }),
                method: 'DELETE',
            }),
            invalidatesTags: (_, _error, { data_product_id }) => [
                { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const, id: data_product_id },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        updateDataset: builder.mutation<
            DatasetUpdateResponse,
            {
                id: string;
                dataset: DatasetUpdateRequest;
            }
        >({
            query: ({ id, dataset }) => ({
                url: buildUrl(ApiUrl.DatasetGet, { datasetId: id }),
                method: 'PUT',
                data: dataset,
            }),
            invalidatesTags: (_, __, { id }) => [
                { type: TagTypes.Dataset as const, id },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.History as const, id },
            ],
        }),
        updateDatasetAbout: builder.mutation<
            void,
            {
                datasetId: string;
                about: string;
            }
        >({
            query: ({ datasetId, about }) => ({
                url: buildUrl(ApiUrl.DatasetAbout, { datasetId }),
                method: 'PUT',
                data: { about },
            }),
            onQueryStarted: async ({ datasetId, about }, { dispatch, queryFulfilled }) => {
                const patchResult = dispatch(
                    datasetsApiSlice.util.updateQueryData('getDatasetById', datasetId as string, (draft) => {
                        draft.about = about;
                    }),
                );

                queryFulfilled.catch(patchResult.undo);
            },
            invalidatesTags: (_, __, { datasetId }) => [
                { type: TagTypes.Dataset as const, id: datasetId },
                { type: TagTypes.History as const, datasetId },
            ],
        }),
        getDatasetGraphData: builder.query<GraphContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DatasetGraph, { datasetId: id }),
                method: 'GET',
            }),
        }),
        validateDatasetNamespace: builder.query<NamespaceValidationResponse, string>({
            query: (namespace) => ({
                url: ApiUrl.DatasetNamespaceValidation,
                method: 'GET',
                params: { namespace },
            }),
        }),
        getDatasetNamespaceSuggestion: builder.query<NamespaceSuggestionResponse, string>({
            query: (name) => ({
                url: ApiUrl.DatasetNamespaceSuggestion,
                method: 'GET',
                params: { name },
            }),
        }),
        getDatasetNamespaceLengthLimits: builder.query<NamespaceLengthLimitsResponse, void>({
            query: () => ({
                url: ApiUrl.DatasetNamespaceLimits,
                method: 'GET',
            }),
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
    useGetDatasetByIdQuery,
    useCreateDatasetMutation,
    useRemoveDatasetMutation,
    useUpdateDatasetMutation,
    useUpdateDatasetAboutMutation,
    useGetUserDatasetsQuery,
    useGetDatasetGraphDataQuery,
    useGetDatasetHistoryQuery,
    useLazyGetDatasetNamespaceSuggestionQuery,
    useLazyValidateDatasetNamespaceQuery,
    useGetDatasetNamespaceLengthLimitsQuery,
    useGetDatasetQueryStatsDailyQuery,
} = datasetsApiSlice;
