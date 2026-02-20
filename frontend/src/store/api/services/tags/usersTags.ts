import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const usersTags = {
    getUsers: {
        providesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.LIST }],
    },
    createUser: {
        invalidatesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.LIST }],
    },
    removeUser: {
        invalidatesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.LIST }],
    },
    setCanBecomeAdmin: {
        invalidatesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.LIST }],
    },
    markTourAsSeen: {
        invalidatesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.CURRENT_USER }],
    },
    getCurrentUser: {
        providesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.CURRENT_USER }],
    },
    getUserPendingActions: {
        providesTags: [{ type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST }],
    },
} satisfies EndpointDefinitions;
