import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { NotificationContract } from '@/types/notifications/notification.contract';

export const notificationsTags: string[] = [
    TagTypes.UserDataProducts,
    TagTypes.UserDatasets,
    TagTypes.UserDataOutputs,
    TagTypes.DataOutput,
    TagTypes.Dataset,
    TagTypes.DataProduct,
    TagTypes.History,
    TagTypes.Notifications,
];

export const notificationsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: notificationsTags }).injectEndpoints({
    endpoints: (builder) => ({
        getNotifications: builder.query<NotificationContract[], void>({
            query: () => ({
                url: buildUrl(ApiUrl.Notifications, {}),
                method: 'GET',
            }),
            providesTags: () => [{ type: TagTypes.Notifications as const, id: STATIC_TAG_ID.LIST }],
        }),
        removeNotification: builder.mutation<void, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.NotificationDelete, { notificationId: id }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.Notifications as const, id: STATIC_TAG_ID.LIST }],
        }),
        removeAllNotifications: builder.mutation<void, void>({
            query: () => ({
                url: buildUrl(ApiUrl.NotificationDeleteAll, {}),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.Notifications as const, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetNotificationsQuery, useRemoveNotificationMutation, useRemoveAllNotificationsMutation } =
    notificationsApiSlice;
