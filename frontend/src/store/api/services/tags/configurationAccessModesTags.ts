import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const configurationAccessModesTags = {
    getAccessModes: {
        providesTags: [{ type: TagTypes.AccessMode, id: STATIC_TAG_ID.LIST }],
    },
    updateAccessMode: {
        invalidatesTags: () => [{ type: TagTypes.AccessMode, id: STATIC_TAG_ID.LIST }],
    },
    createAccessMode: {
        invalidatesTags: () => [{ type: TagTypes.AccessMode, id: STATIC_TAG_ID.LIST }],
    },
} satisfies EndpointDefinitions;
