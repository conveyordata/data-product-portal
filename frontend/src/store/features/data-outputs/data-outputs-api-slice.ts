import { DataOutputsGetContract } from "@/types/data-output/data-output-get.contract";
import { baseApiSlice } from "../api/base-api-slice";
import { ApiUrl } from "@/api/api-urls";
import { DataOutputCreate, DataOutputCreateResponse } from "@/types/data-output";

export const dataOutputsApiSlice = baseApiSlice.enhanceEndpoints({}).injectEndpoints({
    endpoints: (builder) => ({
        getAllDataOutputs: builder.query<DataOutputsGetContract, void>({
            query: () => ({
                url: ApiUrl.DataOutputs,
                method: 'GET',
            })
        }),
        createDataOutput: builder.mutation<DataOutputCreateResponse, DataOutputCreate>({
            query: (dataOutput) => ({
                url: ApiUrl.DataOutputs,
                method: 'POST',
                data: dataOutput,
            }),
        }),
    }),

        overrideExisting: false})


export const {
    useGetAllDataOutputsQuery,
    useCreateDataOutputMutation
} = dataOutputsApiSlice;
