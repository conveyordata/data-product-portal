import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import type {
    DataProductGetConveyorUrlRequest,
    DataProductGetConveyorUrlResponse,
    DataProductGetDatabricksWorkspaceUrlRequest,
    DataProductGetDatabricksWorkspaceUrlResponse,
    DataProductGetSignInUrlRequest,
    DataProductGetSignInUrlResponse,
    DataProductGetSnowflakeUrlRequest,
    DataProductGetSnowflakeUrlResponse,
} from '@/types/data-product';
import type { GraphContract } from '@/types/graph/graph-contract';

export const dataProductsApiSlice = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        getDataProductGraphData: builder.query<GraphContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataProductGraph, { dataProductId: id }),
                method: 'GET',
            }),
        }),
        getDataProductSignInUrl: builder.mutation<DataProductGetSignInUrlResponse, DataProductGetSignInUrlRequest>({
            query: ({ id, environment }) => ({
                url: buildUrl(ApiUrl.DataProductSignInUrl, { dataProductId: id }),
                method: 'GET',
                params: { environment },
            }),
        }),
        getDataProductConveyorIDEUrl: builder.mutation<
            DataProductGetConveyorUrlResponse,
            DataProductGetConveyorUrlRequest
        >({
            query: ({ id }) => ({
                url: buildUrl(ApiUrl.DataProductConveyorIdeUrl, { dataProductId: id }),
                method: 'GET',
            }),
        }),
        getDataProductDatabricksWorkspaceUrl: builder.mutation<
            DataProductGetDatabricksWorkspaceUrlResponse,
            DataProductGetDatabricksWorkspaceUrlRequest
        >({
            query: ({ id, environment }) => ({
                url: buildUrl(ApiUrl.DataProductDatabricksWorkspaceUrl, { dataProductId: id }),
                method: 'GET',
                params: { environment },
            }),
        }),
        getDataProductSnowflakeUrl: builder.mutation<
            DataProductGetSnowflakeUrlResponse,
            DataProductGetSnowflakeUrlRequest
        >({
            query: ({ id, environment }) => ({
                url: buildUrl(ApiUrl.DataProductSnowflakeUrl, { dataProductId: id }),
                method: 'GET',
                params: { environment },
            }),
        }),
    }),
    overrideExisting: false,
});

export const {
    useGetDataProductSignInUrlMutation,
    useGetDataProductConveyorIDEUrlMutation,
    useGetDataProductGraphDataQuery,
    useGetDataProductDatabricksWorkspaceUrlMutation,
    useGetDataProductSnowflakeUrlMutation,
} = dataProductsApiSlice;
