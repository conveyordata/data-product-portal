import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import { GraphContract } from '@/types/graph/graph-contract';

export const graphTags: string[] = [TagTypes.Graph];

export const graphApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: graphTags }).injectEndpoints({
    endpoints: (builder) => ({
        getGraphData: builder.query<GraphContract, string>({
            query: () => ({
                url: ApiUrl.Graph,
                method: 'GET',
            }),
        }),
    }),
    overrideExisting: false,
});

export const { useGetGraphDataQuery } = graphApiSlice;
