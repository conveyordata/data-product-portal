import { ApiUrl } from '@/api/api-urls';
import type { DataOutputResultStringRequest } from '@/types/data-output';
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

export const { useLazyGetDataOutputResultStringQuery } = dataOutputsApiSlice;
