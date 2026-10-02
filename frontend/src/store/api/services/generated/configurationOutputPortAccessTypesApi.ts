import { api } from "@/store/api/services/generated/configurationDataProductTypesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getOutputPortAccessTypes: build.query<
      GetOutputPortAccessTypesApiResponse,
      GetOutputPortAccessTypesApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_access_types`,
        params: {
          include_output_port_count: queryArg,
        },
      }),
    }),
    createOutputPortAccessType: build.mutation<
      CreateOutputPortAccessTypeApiResponse,
      CreateOutputPortAccessTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_access_types`,
        method: "POST",
        body: queryArg,
      }),
    }),
    updateOutputPortAccessType: build.mutation<
      UpdateOutputPortAccessTypeApiResponse,
      UpdateOutputPortAccessTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_access_types/${queryArg.id}`,
        method: "PUT",
        body: queryArg.outputPortAccessTypeUpdate,
      }),
    }),
    removeOutputPortAccessType: build.mutation<
      RemoveOutputPortAccessTypeApiResponse,
      RemoveOutputPortAccessTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_access_types/${queryArg}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetOutputPortAccessTypesApiResponse =
  /** status 200 Successful Response */ OutputPortAccessTypesGet;
export type GetOutputPortAccessTypesApiArg = boolean | undefined;
export type CreateOutputPortAccessTypeApiResponse =
  /** status 200 Successful Response */ CreateOutputPortAccessTypeResponse;
export type CreateOutputPortAccessTypeApiArg = OutputPortAccessTypeCreate;
export type UpdateOutputPortAccessTypeApiResponse =
  /** status 200 Successful Response */ UpdateOutputPortAccessTypeResponse;
export type UpdateOutputPortAccessTypeApiArg = {
  id: string;
  outputPortAccessTypeUpdate: OutputPortAccessTypeUpdate;
};
export type RemoveOutputPortAccessTypeApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveOutputPortAccessTypeApiArg = string;
export type OutputPortAccessTypesGetItem = {
  id: string;
  name: string;
  access_function: OutputPortAccessFunction;
  description: string;
  output_port_count?: number | null;
};
export type OutputPortAccessTypesGet = {
  output_port_access_types: OutputPortAccessTypesGetItem[];
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: any;
  ctx?: object;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type CreateOutputPortAccessTypeResponse = {
  id: string;
};
export type OutputPortAccessTypeCreate = {
  name: string;
  description?: string;
  access_function: OutputPortAccessFunction;
};
export type UpdateOutputPortAccessTypeResponse = {
  id: string;
};
export type OutputPortAccessTypeUpdate = {
  name: string;
  description?: string;
  access_function: OutputPortAccessFunction;
};
export enum OutputPortAccessFunction {
  Restricted = "restricted",
  Private = "private",
  Unrestricted = "unrestricted",
}
export const {
  useGetOutputPortAccessTypesQuery,
  useLazyGetOutputPortAccessTypesQuery,
  useCreateOutputPortAccessTypeMutation,
  useUpdateOutputPortAccessTypeMutation,
  useRemoveOutputPortAccessTypeMutation,
} = injectedRtkApi;
