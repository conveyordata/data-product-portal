import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const accessDurationsTags = {
    getAllAccessDurations: {
        providesTags: [{ type: TagTypes.AccessDuration, id: STATIC_TAG_ID.LIST }],
    },
    updateAccessDuration: {
        invalidatesTags: () => [
            { type: TagTypes.OutputPort },
            { type: TagTypes.DataProductOutputPorts },
            { type: TagTypes.AccessDuration, id: STATIC_TAG_ID.LIST },
        ],
    },
} satisfies EndpointDefinitions;
