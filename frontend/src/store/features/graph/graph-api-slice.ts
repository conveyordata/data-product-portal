import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import { GraphContract } from '@/types/graph/graph-contract';

export const graphTags: string[] = [TagTypes.Graph];

export interface GraphFilterParams {
    includeDataProducts?: boolean;
    includeDatasets?: boolean;
    includeDataOutputs?: boolean;
    includeDomains?: boolean;
}

export const graphApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: graphTags }).injectEndpoints({
    endpoints: (builder) => ({
        getGraphData: builder.query<GraphContract, GraphFilterParams>({
            query: (filters) => ({
                url: ApiUrl.Graph,
                method: 'GET',
                params: {
                    domain_nodes_enabled: String(filters.includeDomains ?? true),
                    data_product_nodes_enabled: String(filters.includeDataProducts ?? true),
                    dataset_nodes_enabled: String(filters.includeDatasets ?? true),
                    data_output_nodes_enabled: String(filters.includeDataOutputs ?? true),
                },
            }),
        }),
    }),
    overrideExisting: false,
});

export const { useGetGraphDataQuery } = graphApiSlice;
