import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const identitiesTags = {
    getGroups: {
        providesTags: [TagTypes.Group],
    },
    getGroup: {
        providesTags: [TagTypes.Group],
    },
    createGroup: {
        invalidatesTags: [TagTypes.Group],
    },
    updateGroup: {
        invalidatesTags: [TagTypes.Group],
    },
    deleteGroup: {
        invalidatesTags: [TagTypes.Group],
    },
    createGroupsBatch: {
        invalidatesTags: [TagTypes.Group],
    },
    deleteGroupsBatch: {
        invalidatesTags: [TagTypes.Group],
    },
    getMachineUsers: {
        providesTags: [TagTypes.MachineUser],
    },
    getMachineUser: {
        providesTags: [TagTypes.MachineUser],
    },
    createMachineUser: {
        invalidatesTags: [TagTypes.MachineUser],
    },
    updateMachineUser: {
        invalidatesTags: [TagTypes.MachineUser],
    },
    deleteMachineUser: {
        invalidatesTags: [TagTypes.MachineUser],
    },
    createMachineUsersBatch: {
        invalidatesTags: [TagTypes.MachineUser],
    },
    deleteMachineUsersBatch: {
        invalidatesTags: [TagTypes.MachineUser],
    },
} satisfies EndpointDefinitions;
