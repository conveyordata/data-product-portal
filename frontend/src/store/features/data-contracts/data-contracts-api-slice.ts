import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { DataContractContract } from '@/types/data-contract';

export const dataContractTags: string[] = [TagTypes.DataContract, TagTypes.DataOutput];

export const dataContractsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: dataContractTags }).injectEndpoints({
    endpoints: (builder) => ({
        getDataContractById: builder.query<DataContractContract, string>({
            query: (dataContractId) => ({
                url: buildUrl(ApiUrl.DataContractGet, { dataContractId }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [{ type: TagTypes.DataContract, id }],
        }),
        getDataContractByOutputId: builder.query<DataContractContract[], string>({
            query: (dataOutputId) => ({
                url: buildUrl(ApiUrl.DataOutputDataContracts, { dataOutputId }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [
                { type: TagTypes.DataOutput, id },
                { type: TagTypes.DataContract, id: STATIC_TAG_ID.LIST },
            ],
        }),
    }),
    overrideExisting: false,
});

export const { useGetDataContractByIdQuery, useGetDataContractByOutputIdQuery } = dataContractsApiSlice;
