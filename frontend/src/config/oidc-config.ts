import { type OidcClientSettings, WebStorageStateStore } from 'oidc-client-ts';
import type { AuthProviderProps } from 'react-oidc-context';

import { AppConfig } from '@/config/app-config.ts';

const oidcCredentials = AppConfig.getOidcCredentials();
export const oidcConfig: OidcClientSettings = {
    ...oidcCredentials,
    loadUserInfo: true,
    scope: 'openid profile email',
};

export const oidcAuthProviderProps: AuthProviderProps = {
    ...oidcConfig,
    automaticSilentRenew: true,
    userStore: new WebStorageStateStore({ store: window.sessionStorage }),
    onSigninCallback: () => {
        window.history.replaceState({}, document.title, window.location.pathname);
    },
};
