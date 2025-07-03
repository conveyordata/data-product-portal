const config = (() => {
    return {
        /**
         * The base URL of the API.
         * This is where the frontend will send API requests.
         */
        API_BASE_URL: 'http://localhost:8080',
        /**
         * Indicates whether OpenID Connect (OIDC) should be enabled.
         * If true, OIDC is enabled.
         */
        OIDC_ENABLED: false,
        /**
         * The client ID for the OIDC provider.
         * This is used to identify the application to the OIDC provider.
         */
        OIDC_CLIENT_ID: '',
        /**
         * The client secret for the OIDC provider.
         * This is used along with the client ID to authenticate the application to the OIDC provider.
         */
        OIDC_CLIENT_SECRET: '',
        /**
         * The URL of the OIDC provider.
         * This is the endpoint where the application will communicate with the OIDC provider.
         */
        OIDC_AUTHORITY: '',
        /**
         * The URL where the OIDC provider will redirect to after successful authentication.
         * This should be a route in the application that handles the authentication response.
         */
        OIDC_REDIRECT_URI: '',
        /**
         * The URL where the OIDC provider will redirect to after successful logout.
         * This should be a route in the application that handles post-logout actions.
         */
        OIDC_POST_LOGOUT_REDIRECT_URI: '',
        /**
         * The Theme configuration for your application.
         * Pick one from blueThemeConfig, datamindedThemeConfig, greenThemeConfig.
         * @description This is used to customize the appearance of your application.
         */
        THEME_CONFIGURATION: 'datamindedthemeconfig',
        /**
         * The PostHog key and host for tracking events.
         * @description This is used to send events to PostHog for analytics.
         */
        POSTHOG_KEY: 'phc_api_key_here', // Replace with your actual PostHog key
        POSTHOG_HOST: 'https://eu.i.posthog.com',
    };
})();
