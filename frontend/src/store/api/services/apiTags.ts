import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';

api.enhanceEndpoints({
    addTagTypes: [TagTypes.DataProduct, TagTypes.History],

    endpoints: {
        getDataProduct: {
            providesTags: (_, __, { id }) => [{ type: TagTypes.DataProduct, id }],
        },
        updateDataProductAbout: {
            invalidatesTags: (_, __, { id }) => [
                { type: TagTypes.DataProduct, id },
                { type: TagTypes.History, id },
            ],
        },
    },
});
