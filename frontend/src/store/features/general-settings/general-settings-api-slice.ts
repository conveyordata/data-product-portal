import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import { GeneralSettings, GeneralSettingsUpdateRequest } from '@/types/general-settings';

export const generalSettingsTags: string[] = [TagTypes.GeneralSettings];
export const generalSettingsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: generalSettingsTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getGeneralSettings: builder.query<GeneralSettings, void>({
                query: () => ({
                    url: ApiUrl.GeneralSettings,
                    method: 'GET',
                }),
                providesTags: [{ type: TagTypes.GeneralSettings }],
            }),
            updateGeneralSettings: builder.mutation<GeneralSettings, GeneralSettingsUpdateRequest>({
                query: (request) => ({
                    url: ApiUrl.GeneralSettings,
                    method: 'PUT',
                    data: request,
                }),
                invalidatesTags: [{ type: TagTypes.GeneralSettings }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetGeneralSettingsQuery, useUpdateGeneralSettingsMutation } = generalSettingsApiSlice;
