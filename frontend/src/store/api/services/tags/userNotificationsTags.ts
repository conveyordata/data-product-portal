import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const userNotificationsTags = {
    getUserNotifications: {
        providesTags: [{ type: TagTypes.Notifications, id: STATIC_TAG_ID.CURRENT_USER }],
    },
    removeAllUserNotifications: {
        invalidatesTags: [{ type: TagTypes.Notifications, id: STATIC_TAG_ID.CURRENT_USER }],
    },
    removeUserNotification: {
        invalidatesTags: [{ type: TagTypes.Notifications, id: STATIC_TAG_ID.CURRENT_USER }],
    },
} satisfies EndpointDefinitions;
