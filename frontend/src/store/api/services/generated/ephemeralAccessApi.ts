import { api } from "@/store/api/services/generated/versionApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    listEphemeralAccess: build.query<
      ListEphemeralAccessApiResponse,
      ListEphemeralAccessApiArg
    >({
      query: () => ({ url: `/api/v2/ephemeral_access` }),
    }),
    createEphemeralAccess: build.mutation<
      CreateEphemeralAccessApiResponse,
      CreateEphemeralAccessApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/ephemeral_access`,
        method: "POST",
        body: queryArg,
      }),
    }),
    addOutputPortsToEphemeral: build.mutation<
      AddOutputPortsToEphemeralApiResponse,
      AddOutputPortsToEphemeralApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/ephemeral_access/${queryArg.id}/output_ports`,
        method: "POST",
        body: queryArg.addOutputPortsToEphemeral,
      }),
    }),
    revokeEphemeralAccess: build.mutation<
      RevokeEphemeralAccessApiResponse,
      RevokeEphemeralAccessApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/ephemeral_access/${queryArg}`,
        method: "DELETE",
      }),
    }),
    promoteEphemeralAccess: build.mutation<
      PromoteEphemeralAccessApiResponse,
      PromoteEphemeralAccessApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/ephemeral_access/${queryArg}/promote`,
        method: "POST",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type ListEphemeralAccessApiResponse =
  /** status 200 Successful Response */ EphemeralAccessResponse[];
export type ListEphemeralAccessApiArg = void;
export type CreateEphemeralAccessApiResponse =
  /** status 200 Successful Response */ CreateEphemeralAccessResponse;
export type CreateEphemeralAccessApiArg = EphemeralDataProductCreate;
export type AddOutputPortsToEphemeralApiResponse =
  /** status 200 Successful Response */ any;
export type AddOutputPortsToEphemeralApiArg = {
  id: string;
  addOutputPortsToEphemeral: AddOutputPortsToEphemeral;
};
export type RevokeEphemeralAccessApiResponse = unknown;
export type RevokeEphemeralAccessApiArg = string;
export type PromoteEphemeralAccessApiResponse =
  /** status 200 Successful Response */ PromoteEphemeralAccessResponse;
export type PromoteEphemeralAccessApiArg = string;
export type Domain = {
  id: string;
  name: string;
  description: string;
};
export type EphemeralAccessPortResponse = {
  id: string;
  output_port_id: string;
  output_port_name: string;
  status: DecisionStatus;
  data_product_id: string;
};
export type EphemeralAccessResponse = {
  id: string;
  name: string;
  description: string;
  status: DataProductStatus;
  is_ephemeral: boolean;
  expires_at: string | null;
  ttl_hours: number | null;
  domain: Domain;
  input_ports: EphemeralAccessPortResponse[];
};
export type CreateEphemeralAccessResponse = {
  id: string;
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
export type EphemeralDataProductCreate = {
  output_port_ids: string[];
  ttl_hours?: number;
  justification?: string | null;
  name?: string | null;
};
export type AddOutputPortsToEphemeral = {
  output_port_ids: string[];
};
export type PromoteEphemeralAccessResponse = {
  id: string;
};
export enum DataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum DecisionStatus {
  Approved = "approved",
  Pending = "pending",
  Denied = "denied",
}
export const {
  useListEphemeralAccessQuery,
  useLazyListEphemeralAccessQuery,
  useCreateEphemeralAccessMutation,
  useAddOutputPortsToEphemeralMutation,
  useRevokeEphemeralAccessMutation,
  usePromoteEphemeralAccessMutation,
} = injectedRtkApi;
