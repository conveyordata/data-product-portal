import type { ThemeConfig } from 'antd';
import type { OidcClientSettings } from 'oidc-client-ts';

import { blueThemeConfig, datamindedThemeConfig, greenThemeConfig } from '@/theme/antd-theme';
import type { LogoutCognitoExtraParams } from '@/types/auth/oidc.ts';

interface Config {
    /**
     * The base URL of your API.
     * @description This is where your frontend will send API requests.
     */
    API_BASE_URL: string;
    /**
     * Indicates whether OpenID Connect (OIDC) is disabled.
     * @description If true, OIDC is disabled.
     */
    OIDC_ENABLED: boolean;
    /**
     * The client ID for your OIDC provider.
     * @description This is used to identify your application to the OIDC provider.
     */
    OIDC_CLIENT_ID: string;
    /**
     * The client secret for your OIDC provider.
     * @description This is used along with the client ID to authenticate your application to the OIDC provider.
     */
    OIDC_CLIENT_SECRET: string;
    /**
     * The URL of your OIDC provider.
     * @description This is the endpoint where your application will communicate with the OIDC provider.
     */
    OIDC_AUTHORITY: string;
    /**
     * The URL where the OIDC provider will redirect to after successful authentication.
     * @description This should be a route in your application that handles the authentication response.
     */
    OIDC_REDIRECT_URI: string;
    /**
     * The URL where the OIDC provider will redirect to after successful logout.
     * @description This should be a route in your application that handles post-logout actions.
     */
    OIDC_POST_LOGOUT_REDIRECT_URI: string;
    /**
     * The Theme configuration for your application.
     * Pick one from blueThemeConfig, datamindedThemeConfig, greenThemeConfig.
     * @description This is used to customize the appearance of your application.
     */
    THEME_CONFIGURATION: string;

    /**
     * The PostHog key and host for tracking events.
     * @description This is used to send events to PostHog for analytics.
     */
    POSTHOG_KEY: string;
    POSTHOG_HOST: string;
}

declare global {
    const config: Config;
}

// biome-ignore lint/complexity/noStaticOnlyClass: Fine for the config
export class AppConfig {
    public static getThemeConfiguration(): ThemeConfig {
        const themeMapping: Record<string, ThemeConfig> = {
            bluethemeconfig: blueThemeConfig,
            datamindedthemeconfig: datamindedThemeConfig,
            greenthemeconfig: greenThemeConfig,
        };
        const theme = themeMapping[config.THEME_CONFIGURATION.toLowerCase()];
        if (!theme) {
            throw new Error(`Invalid theme configuration: ${config.THEME_CONFIGURATION}`);
        }

        return theme;
    }

    public static getApiBaseURL(): string {
        return config.API_BASE_URL;
    }

    public static isOidcEnabled(): boolean {
        return config.OIDC_ENABLED;
    }

    public static getOidcCognitoLogoutParams() {
        const params: LogoutCognitoExtraParams = {
            client_id: config.OIDC_CLIENT_ID,
            redirect_uri: config.OIDC_REDIRECT_URI,
            logout_uri: config.OIDC_POST_LOGOUT_REDIRECT_URI,
            response_type: 'code',
        };

        return params;
    }

    public static getOidcCredentials(): Pick<
        OidcClientSettings,
        'authority' | 'client_id' | 'client_secret' | 'redirect_uri' | 'post_logout_redirect_uri'
    > {
        return {
            authority: config.OIDC_AUTHORITY,
            client_id: config.OIDC_CLIENT_ID,
            client_secret: config.OIDC_CLIENT_SECRET,
            post_logout_redirect_uri: config.OIDC_POST_LOGOUT_REDIRECT_URI,
            redirect_uri: config.OIDC_REDIRECT_URI,
        };
    }
}
