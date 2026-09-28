import { api } from "@/store/api/services/generated/configurationDataProductTypesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getOutputPortClassifications: build.query<
      GetOutputPortClassificationsApiResponse,
      GetOutputPortClassificationsApiArg
    >({
      query: () => ({
        url: `/api/v2/configuration/output_port_classifications`,
      }),
    }),
    createOutputPortClassification: build.mutation<
      CreateOutputPortClassificationApiResponse,
      CreateOutputPortClassificationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_classifications`,
        method: "POST",
        body: queryArg,
      }),
    }),
    updateOutputPortClassification: build.mutation<
      UpdateOutputPortClassificationApiResponse,
      UpdateOutputPortClassificationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_classifications/${queryArg.id}`,
        method: "PUT",
        body: queryArg.outputPortClassificationUpdate,
      }),
    }),
    removeOutputPortClassification: build.mutation<
      RemoveOutputPortClassificationApiResponse,
      RemoveOutputPortClassificationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/output_port_classifications/${queryArg}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetOutputPortClassificationsApiResponse =
  /** status 200 Successful Response */ OutputPortClassificationsGet;
export type GetOutputPortClassificationsApiArg = void;
export type CreateOutputPortClassificationApiResponse =
  /** status 200 Successful Response */ CreateOutputPortClassificationResponse;
export type CreateOutputPortClassificationApiArg =
  OutputPortClassificationCreate;
export type UpdateOutputPortClassificationApiResponse =
  /** status 200 Successful Response */ UpdateOutputPortClassificationResponse;
export type UpdateOutputPortClassificationApiArg = {
  id: string;
  outputPortClassificationUpdate: OutputPortClassificationUpdate;
};
export type RemoveOutputPortClassificationApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveOutputPortClassificationApiArg = string;
export type OutputPortClassificationsGetItem = {
  id: string;
  name: string;
  access_type: OutputPortAccessType;
  description: string;
  output_port_count: number;
};
export type OutputPortClassificationsGet = {
  output_port_classifications: OutputPortClassificationsGetItem[];
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
export type CreateOutputPortClassificationResponse = {
  id: string;
};
export type OutputPortClassificationCreate = {
  name: string;
  description?: string;
  access_type: OutputPortAccessType;
};
export type UpdateOutputPortClassificationResponse = {
  id: string;
};
export type OutputPortClassificationUpdate = {
  name: string;
  description?: string;
  access_type: OutputPortAccessType;
};
export enum OutputPortAccessType {
  Restricted = "restricted",
  Private = "private",
  Unrestricted = "unrestricted",
}
export const {
  useGetOutputPortClassificationsQuery,
  useLazyGetOutputPortClassificationsQuery,
  useCreateOutputPortClassificationMutation,
  useUpdateOutputPortClassificationMutation,
  useRemoveOutputPortClassificationMutation,
} = injectedRtkApi;
