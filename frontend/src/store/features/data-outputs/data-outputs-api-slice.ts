import { ApiUrl, buildUrl } from '@/api/api-urls';
import type { DataOutputResultStringRequest } from '@/types/data-output';
import type { GraphContract } from '@/types/graph/graph-contract';
import { baseApiSlice } from '../api/base-api-slice';
import { TagTypes } from '../api/tag-types';

export const dataOutputTags: string[] = [
    TagTypes.DataOutput,
    TagTypes.UserDataProducts,
    TagTypes.DataProduct,
    TagTypes.UserDatasets,
    TagTypes.UserDataOutputs,
    TagTypes.History,
];

export const dataOutputsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: dataOutputTags }).injectEndpoints({
    endpoints: (builder) => ({
        getDataOutputGraphData: builder.query<GraphContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputGraph, { dataOutputId: id }),
                method: 'GET',
            }),
        }),
        getDataOutputResultString: builder.query<string, DataOutputResultStringRequest>({
            query: (data) => ({
                url: ApiUrl.DataOutputResultString,
                method: 'POST',
                data,
            }),
        }),
    }),

    overrideExisting: false,
});

export const { useGetDataOutputGraphDataQuery, useLazyGetDataOutputResultStringQuery } = dataOutputsApiSlice;
