import { api } from '@/store/api/services/generated/graphApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getUserNotificationsApiNotificationsGet: build.query<
            GetUserNotificationsApiNotificationsGetApiResponse,
            GetUserNotificationsApiNotificationsGetApiArg
        >({
            query: () => ({ url: '/api/notifications' }),
        }),
        removeAllUserNotificationsApiNotificationsAllDelete: build.mutation<
            RemoveAllUserNotificationsApiNotificationsAllDeleteApiResponse,
            RemoveAllUserNotificationsApiNotificationsAllDeleteApiArg
        >({
            query: () => ({ url: '/api/notifications/all', method: 'DELETE' }),
        }),
        removeUserNotificationApiNotificationsIdDelete: build.mutation<
            RemoveUserNotificationApiNotificationsIdDeleteApiResponse,
            RemoveUserNotificationApiNotificationsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/notifications/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetUserNotificationsApiNotificationsGetApiResponse =
    /** status 200 Successful Response */ NotificationGet[];
export type GetUserNotificationsApiNotificationsGetApiArg = void;
export type RemoveAllUserNotificationsApiNotificationsAllDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveAllUserNotificationsApiNotificationsAllDeleteApiArg = void;
export type RemoveUserNotificationApiNotificationsIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveUserNotificationApiNotificationsIdDeleteApiArg = {
    id: string;
};
export type EventReferenceEntity = 'data_product' | 'dataset' | 'data_output' | 'user';
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
};
export type DataProductStatus = 'pending' | 'active' | 'archived';
export type DataProductIconKey =
    | 'reporting'
    | 'processing'
    | 'exploration'
    | 'ingestion'
    | 'machine_learning'
    | 'analytics'
    | 'default';
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
    status: DataProductStatus;
    type: DataProductType;
};
export type DatasetStatus = 'pending' | 'active' | 'archived';
export type DatasetAccessType = 'public' | 'restricted' | 'private';
export type Dataset = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DatasetStatus;
    access_type: DatasetAccessType;
};
export type DataOutputStatus = 'pending' | 'active' | 'archived';
export type DatabricksDataOutput = {
    configuration_type: 'DatabricksDataOutput';
    catalog: string;
    schema?: string;
    table?: string;
    bucket_identifier?: string;
    catalog_path?: string;
    table_path?: string;
};
export type GlueDataOutput = {
    configuration_type: 'GlueDataOutput';
    database: string;
    database_suffix?: string;
    table?: string;
    bucket_identifier?: string;
    database_path?: string;
    table_path?: string;
};
export type RedshiftDataOutput = {
    configuration_type: 'RedshiftDataOutput';
    database: string;
    schema?: string;
    table?: string;
    bucket_identifier?: string;
    database_path?: string;
    table_path?: string;
};
export type S3DataOutput = {
    configuration_type: 'S3DataOutput';
    bucket: string;
    suffix?: string;
    path: string;
};
export type SnowflakeDataOutput = {
    configuration_type: 'SnowflakeDataOutput';
    database: string;
    schema?: string;
    table?: string;
    bucket_identifier?: string;
    database_path?: string;
    table_path?: string;
};
export type DataOutput = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DataOutputStatus;
    sourceAligned: boolean | null;
    owner_id: string;
    platform_id: string;
    service_id: string;
    configuration:
        | ({
              configuration_type: 'DatabricksDataOutput';
          } & DatabricksDataOutput)
        | ({
              configuration_type: 'GlueDataOutput';
          } & GlueDataOutput)
        | ({
              configuration_type: 'RedshiftDataOutput';
          } & RedshiftDataOutput)
        | ({
              configuration_type: 'S3DataOutput';
          } & S3DataOutput)
        | ({
              configuration_type: 'SnowflakeDataOutput';
          } & SnowflakeDataOutput);
};
export type EventGet = {
    id: string;
    name: string;
    subject_id: string;
    target_id?: string | null;
    subject_type: EventReferenceEntity;
    target_type?: EventReferenceEntity | null;
    actor_id: string;
    created_on: string;
    deleted_subject_identifier?: string | null;
    deleted_target_identifier?: string | null;
    actor: User;
    data_product?: DataProduct | null;
    user?: User | null;
    dataset?: Dataset | null;
    data_output?: DataOutput | null;
};
export type NotificationGet = {
    id: string;
    event_id: string;
    user_id: string;
    event: EventGet;
    user: User;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export const {
    useGetUserNotificationsApiNotificationsGetQuery,
    useLazyGetUserNotificationsApiNotificationsGetQuery,
    useRemoveAllUserNotificationsApiNotificationsAllDeleteMutation,
    useRemoveUserNotificationApiNotificationsIdDeleteMutation,
} = injectedRtkApi;
