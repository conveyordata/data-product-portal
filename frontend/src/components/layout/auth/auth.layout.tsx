import { useCallback, useEffect } from 'react';
import { useAuth } from 'react-oidc-context';
import { useSelector } from 'react-redux';
import { Outlet, useLocation, useNavigate } from 'react-router';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { AppConfig } from '@/config/app-config.ts';
import { useAppDispatch } from '@/store';
import { useAuthorizeMutation } from '@/store/features/auth/auth-api-slice.ts';
import { selectAuthState, setCredentials } from '@/store/features/auth/auth-slice.ts';

const oidcCognitoParams = AppConfig.getOidcCognitoLogoutParams();

export const AuthLayout = () => {
    const [authorizeUser] = useAuthorizeMutation();
    const navigate = useNavigate();
    const location = useLocation();
    const isOidcEnabled = AppConfig.isOidcEnabled();
    const dispatch = useAppDispatch();
    const { isAuthenticated, isLoading, signinRedirect, events, activeNavigator, signoutRedirect, signinSilent } =
        useAuth();
    const { isLoading: isSettingUserCredentialsInStore, user } = useSelector(selectAuthState);

    const redirectToSignIn = useCallback(async () => {
        const originalPath = location.pathname + location.search + location.hash;
        sessionStorage.setItem('redirectAfterLogin', originalPath);
        await signinRedirect();
    }, [location, signinRedirect]);

    const handleAuthorizeUser = useCallback(async () => {
        try {
            const authorizedUser = await authorizeUser().unwrap();
            if (authorizedUser) {
                dispatch(setCredentials({ user: authorizedUser }));
            }
        } catch (e) {
            console.error('Failed to authorize user', e);
        }
    }, [authorizeUser, dispatch]);

    useEffect(() => {
        if (isOidcEnabled && !isLoading) {
            if (isAuthenticated) {
                handleAuthorizeUser().then(() => {
                    const redirectPath = sessionStorage.getItem('redirectAfterLogin');
                    sessionStorage.removeItem('redirectAfterLogin');
                    if (redirectPath) {
                        navigate(redirectPath);
                    }
                });
            } else {
                redirectToSignIn().catch((e) => {
                    console.error('Failed to sign in', e);
                });
            }
        }
    }, [handleAuthorizeUser, isAuthenticated, isLoading, isOidcEnabled, navigate, redirectToSignIn]);

    useEffect(() => {
        if (!isOidcEnabled && !user) {
            handleAuthorizeUser().then(() => {
                navigate({ search: '' });
            });
        }
    }, [handleAuthorizeUser, isOidcEnabled, navigate, user]);

    useEffect(() => {
        // This gets called when the user is authenticated
        events.addUserLoaded(async () => {
            try {
                await handleAuthorizeUser();
            } catch (_e) {
                await signoutRedirect({
                    extraQueryParams: {
                        ...oidcCognitoParams,
                    },
                });
            }
        });

        events.addAccessTokenExpiring(async () => {
            await signinSilent({
                extraQueryParams: {
                    ...oidcCognitoParams,
                },
            });
        });

        events.addAccessTokenExpired(async () => {
            await signoutRedirect({
                extraQueryParams: {
                    ...oidcCognitoParams,
                },
            });
        });
    }, [events, handleAuthorizeUser, signinSilent, signoutRedirect]);

    if (activeNavigator) {
        switch (activeNavigator) {
            case 'signinRedirect':
            case 'signoutRedirect':
            case 'signoutSilent':
                return <LoadingSpinner />;
            case 'signinSilent':
                return <Outlet />;
        }
    }

    if (isLoading || isSettingUserCredentialsInStore) {
        return <LoadingSpinner />;
    }
    if (!isOidcEnabled || isAuthenticated) {
        return <Outlet />;
    }
    return null;
};
