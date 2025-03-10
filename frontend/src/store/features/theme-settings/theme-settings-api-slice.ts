import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import { ThemeSettings, ThemeSettingsUpdateRequest } from '@/types/theme-settings';

export const ThemeSettingsTags: string[] = [TagTypes.ThemeSettings];
export const ThemeSettingsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: ThemeSettingsTags }).injectEndpoints({
    endpoints: (builder) => ({
        getThemeSettings: builder.query<ThemeSettings, void>({
            query: () => ({
                url: ApiUrl.ThemeSettings,
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.ThemeSettings }],
        }),
        updateThemeSettings: builder.mutation<ThemeSettings, ThemeSettingsUpdateRequest>({
            query: (request) => ({
                url: ApiUrl.ThemeSettings,
                method: 'PUT',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.ThemeSettings }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetThemeSettingsQuery, useUpdateThemeSettingsMutation } = ThemeSettingsApiSlice;
