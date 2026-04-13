import { api } from "@/store/api/services/generated/configurationPlatformsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getThemeSettings: build.query<
      GetThemeSettingsApiResponse,
      GetThemeSettingsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/theme_settings` }),
    }),
    updateThemeSettings: build.mutation<
      UpdateThemeSettingsApiResponse,
      UpdateThemeSettingsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/theme_settings`,
        method: "PUT",
        body: queryArg,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetThemeSettingsApiResponse =
  /** status 200 Successful Response */ ThemeSettings;
export type GetThemeSettingsApiArg = void;
export type UpdateThemeSettingsApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateThemeSettingsApiArg = ThemeSettings;
export type ThemeSettings = {
  portal_name: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: any;
  ctx?: object;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export const {
  useGetThemeSettingsQuery,
  useLazyGetThemeSettingsQuery,
  useUpdateThemeSettingsMutation,
} = injectedRtkApi;
