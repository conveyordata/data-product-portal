import { api } from '@/store/api/services/generated/roleAssignmentsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getSettingsApiThemeSettingsGet: build.query<
            GetSettingsApiThemeSettingsGetApiResponse,
            GetSettingsApiThemeSettingsGetApiArg
        >({
            query: () => ({ url: '/api/theme_settings' }),
        }),
        updateSettingsApiThemeSettingsPut: build.mutation<
            UpdateSettingsApiThemeSettingsPutApiResponse,
            UpdateSettingsApiThemeSettingsPutApiArg
        >({
            query: (queryArg) => ({
                url: '/api/theme_settings',
                method: 'PUT',
                body: queryArg.themeSettings,
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetSettingsApiThemeSettingsGetApiResponse = /** status 200 Successful Response */ ThemeSettings;
export type GetSettingsApiThemeSettingsGetApiArg = void;
export type UpdateSettingsApiThemeSettingsPutApiResponse = /** status 200 Successful Response */ any;
export type UpdateSettingsApiThemeSettingsPutApiArg = {
    themeSettings: ThemeSettings;
};
export type ThemeSettings = {
    portal_name: string;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export const {
    useGetSettingsApiThemeSettingsGetQuery,
    useLazyGetSettingsApiThemeSettingsGetQuery,
    useUpdateSettingsApiThemeSettingsPutMutation,
} = injectedRtkApi;
