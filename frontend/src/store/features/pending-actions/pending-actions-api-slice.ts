import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { PendingAction } from '@/types/pending-actions/pending-actions';

export const pendingActionsTags: string[] = [
    TagTypes.DataProduct,
    TagTypes.Dataset,
    TagTypes.UserDataProducts,
    TagTypes.UserDatasets,
    TagTypes.Role,
];
export const pendingActionsDatasetsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: pendingActionsTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getPendingActions: builder.query<PendingAction[], void>({
                query: () => ({
                    url: buildUrl(ApiUrl.PendingActions, {}),
                    method: 'GET',
                }),
                providesTags: () => [
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetPendingActionsQuery } = pendingActionsDatasetsApiSlice;
