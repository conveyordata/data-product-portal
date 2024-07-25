import { DataOutputsGetContract } from "@/types/data-output/data-output-get.contract";
import { baseApiSlice } from "../api/base-api-slice";
import { ApiUrl } from "@/api/api-urls";
import { DataOutputCreate, DataOutputCreateResponse } from "@/types/data-output";
import { STATIC_TAG_ID, TagTypes } from "../api/tag-types";

export const dataOutputTags: string[] = [
    TagTypes.DataOutput,
    TagTypes.UserDataProducts,
    TagTypes.DataProduct,
    TagTypes.UserDatasets,
];

export const dataOutputsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: dataOutputTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllDataOutputs: builder.query<DataOutputsGetContract, void>({
            query: () => ({
                url: ApiUrl.DataOutputs,
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST }],
        }),
        createDataOutput: builder.mutation<DataOutputCreateResponse, DataOutputCreate>({
            query: (dataOutput) => ({
                url: ApiUrl.DataOutputs,
                method: 'POST',
                data: dataOutput,
            }),
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const, id: arg.owner_id },
            ],
            // invalidatesTags: (_, _error, arg) => [
            //
            //     { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
            //     { type: TagTypes.DataOutput as const, id: arg.dataOutputId },
            //     { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            // ],
        }),
    }),

        overrideExisting: false})


export const {
    useGetAllDataOutputsQuery,
    useCreateDataOutputMutation
} = dataOutputsApiSlice;
