import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const dataProductsToolsTags = {
    getDataProductTools: {
        providesTags: [{ type: TagTypes.Tool, id: STATIC_TAG_ID.LIST }],
    },
    getTool: {
        providesTags: (_result, _error, { id }) => [{ type: TagTypes.Tool, id }],
    },
    createTool: {
        invalidatesTags: () => [{ type: TagTypes.Tool, id: STATIC_TAG_ID.LIST }],
    },
    deleteTool: {
        invalidatesTags: () => [{ type: TagTypes.Tool, id: STATIC_TAG_ID.LIST }],
    },
    getToolEnvironmentConfiguration: {
        providesTags: (_result, _error, { id }) => [{ type: TagTypes.Tool, id }],
    },
    updateToolEnvironmentConfiguration: {
        invalidatesTags: (_result, _error, { id }) => [
            { type: TagTypes.Tool, id },
            { type: TagTypes.Tool, id: STATIC_TAG_ID.LIST },
        ],
    },
    getPlatformEnvironmentSettings: {
        providesTags: (_result, _error, { platformKey, environmentId }) => [
            { type: TagTypes.Platform, id: `${platformKey}-${environmentId}` },
        ],
    },
    updatePlatformEnvironmentSettings: {
        invalidatesTags: (_result, _error, { platformKey, environmentId }) => [
            { type: TagTypes.Platform, id: `${platformKey}-${environmentId}` },
        ],
    },
} satisfies EndpointDefinitions;
