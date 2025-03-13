import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import { NotificationModel } from '@/types/notifications/notification.contract';

export const notificationsTags: string[] = [
    //TODO
    TagTypes.DataOutput,
    TagTypes.Dataset,
    TagTypes.DataProduct,
];
export const notificationsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: notificationsTags }).injectEndpoints({
    endpoints: (builder) => ({
        getNotifications: builder.query<NotificationModel[], void>({
            query: () => ({
                url: buildUrl(ApiUrl.Notifications, {}),
                method: 'GET',
            }),
            // Comment out or remove the following line to disable tags:
            // providesTags: () => [
            //     { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
            //     { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            // ],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetNotificationsQuery } = notificationsApiSlice;
