import { api } from "@/store/api/services/generated/usersApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    removeAllUserNotifications: build.mutation<
      RemoveAllUserNotificationsApiResponse,
      RemoveAllUserNotificationsApiArg
    >({
      query: () => ({
        url: `/api/v2/users/current/notifications/all`,
        method: "DELETE",
      }),
    }),
    removeUserNotification: build.mutation<
      RemoveUserNotificationApiResponse,
      RemoveUserNotificationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/users/current/notifications/${queryArg}`,
        method: "DELETE",
      }),
    }),
    getUserNotifications: build.query<
      GetUserNotificationsApiResponse,
      GetUserNotificationsApiArg
    >({
      query: () => ({ url: `/api/v2/users/current/notifications` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type RemoveAllUserNotificationsApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveAllUserNotificationsApiArg = void;
export type RemoveUserNotificationApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveUserNotificationApiArg = string;
export type GetUserNotificationsApiResponse =
  /** status 200 Successful Response */ GetUserNotificationsResponse;
export type GetUserNotificationsApiArg = void;
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
export type User = {
  id: string;
  email: string;
  external_id: string;
  first_name: string;
  last_name: string;
  has_seen_tour: boolean;
  can_become_admin: boolean;
  admin_expiry?: string | null;
};
export type DataProductType = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProduct = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: AbstractDataProductStatus;
  type: DataProductType;
};
export type Tag = {
  id: string;
  value: string;
};
export type AccessMode = {
  id: string;
  name: string;
  description: string;
};
export type OutputPort = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: OutputPortStatus;
  access_type: OutputPortAccessType;
  data_product_id: string;
  tags: Tag[];
  access_modes: AccessMode[];
};
export type TechnicalAsset = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: TechnicalAssetStatus;
  technical_mapping: TechnicalMapping;
  owner_id: string;
  platform_id?: string | null;
  service_id?: string | null;
  /** Configuration of the technical asset. The available fields depend on `name`; retrieve them from /v2/plugins/{name}/form. */
  configuration: {
    name: string;
    [key: string]: any;
  };
};
export type GetEventHistoryResponseItem = {
  id: string;
  name: string;
  subject_id: string;
  target_id?: string | null;
  subject_type: EventEntityType;
  target_type?: EventEntityType | null;
  actor_id: string;
  created_on: string;
  deleted_subject_identifier?: string | null;
  deleted_target_identifier?: string | null;
  actor: User;
  data_product?: DataProduct | null;
  user?: User | null;
  output_port?: OutputPort | null;
  technical_asset?: TechnicalAsset | null;
};
export type GetUserNotificationsResponseItem = {
  id: string;
  event_id: string;
  user_id: string;
  event: GetEventHistoryResponseItem;
  user: User;
};
export type GetUserNotificationsResponse = {
  notifications: GetUserNotificationsResponseItem[];
};
export enum EventEntityType {
  DataProduct = "data_product",
  OutputPort = "output_port",
  TechnicalAsset = "technical_asset",
  User = "user",
}
export enum AbstractDataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
  Deleting = "deleting",
}
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
}
export enum OutputPortStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum OutputPortAccessType {
  Restricted = "restricted",
  Private = "private",
  Unrestricted = "unrestricted",
}
export enum TechnicalAssetStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum TechnicalMapping {
  Default = "default",
  Custom = "custom",
}
export const {
  useRemoveAllUserNotificationsMutation,
  useRemoveUserNotificationMutation,
  useGetUserNotificationsQuery,
  useLazyGetUserNotificationsQuery,
} = injectedRtkApi;
