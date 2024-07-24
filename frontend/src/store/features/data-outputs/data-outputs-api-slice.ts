import { DataOutputsGetContract } from "@/types/data-output/data-output-get-contract";
import { baseApiSlice } from "../api/base-api-slice";
import { ApiUrl } from "@/api/api-urls";

export const dataOutputsApiSlice = baseApiSlice.enhanceEndpoints({}).injectEndpoints({
    endpoints: (builder) => ({
        getAllDataOutputs: builder.query<DataOutputsGetContract, void>({
            query: () => ({
                url: ApiUrl.Datasets,
                method: 'GET',
            })
        })}),

        overrideExisting: false})


export const {
    useGetAllDataOutputsQuery
} = dataOutputsApiSlice;
