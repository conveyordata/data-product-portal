import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { DataContractContract } from '@/types/data-contract';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';

export const dataContractTags: string[] = [
    TagTypes.DataContract,
    TagTypes.DataOutput,
];

export const dataContractsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: dataContractTags }).injectEndpoints({
    endpoints: (builder) => ({
        getDataContractByOutputId: builder.query<DataContractContract[], string>({
            query: (dataOutputId) => ({
                url: buildUrl(ApiUrl.getDataContractByOutputId, { dataOutputId }),
                method: 'GET',
            }),
            providesTags: (_, __, id ) => [
                { type: TagTypes.DataOutput, id},
                { type: TagTypes.DataContract, id: STATIC_TAG_ID.LIST},
            ]
        }),
    }),
    overrideExisting: false,
});

export const {
    useGetDataContractByOutputIdQuery,
} = dataContractsApiSlice;
