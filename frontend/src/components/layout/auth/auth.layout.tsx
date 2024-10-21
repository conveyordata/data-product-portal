import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';
import { useEffect } from 'react';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { AppConfig } from '@/config/app-config.ts';
import { useAuthorizeMutation } from '@/store/features/auth/auth-api-slice.ts';
import { useAppDispatch } from '@/store';
import { selectAuthState, setCredentials } from '@/store/features/auth/auth-slice.ts';
import { useSelector } from 'react-redux';

const oidcCognitoParams = AppConfig.getOidcCognitoLogoutParams();

export const AuthLayout = () => {
    const [authorizeUser] = useAuthorizeMutation();
    const navigate = useNavigate();
    const isOidcEnabled = AppConfig.isOidcEnabled();
    const dispatch = useAppDispatch();
    const { isAuthenticated, isLoading, signinRedirect, events, activeNavigator, signoutRedirect, signinSilent } =
        useAuth();
    const { isLoading: isSettingUserCredentialsInStore, user } = useSelector(selectAuthState);
    const redirectToSignIn = async () => {
        await signinRedirect();
    };

    const handleAuthorizeUser = async () => {
        try {
            const authorizedUser = await authorizeUser().unwrap();
            if (authorizedUser) {
                dispatch(
                    setCredentials({
                        user: authorizedUser,
                    }),
                );
            }
        } catch (_e) {
            console.error('Failed to authorize user', e);
        }
    };
    useEffect(() => {
        if (isOidcEnabled) {
            if (!isLoading) {
                if (isAuthenticated) {
                    handleAuthorizeUser().then(() => {
                        navigate({ search: '' });
                    });
                } else {
                    redirectToSignIn().catch((e) => {
                        console.error('Failed to sign in', e);
                    });
                }
            }
        } else {
            if (!user) {
                handleAuthorizeUser().then(() => {
                    navigate({ search: '' });
                });
            }
        }
    }, [isAuthenticated, isLoading]);

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
    }, [events]);

    if (activeNavigator) {
        switch (activeNavigator) {
            case 'signinRedirect':
            case 'signoutRedirect':
                return <LoadingSpinner />;
        }
    }

    if (isLoading || isSettingUserCredentialsInStore) {
        return <LoadingSpinner />;
    } else {
        if (!isOidcEnabled || isAuthenticated) {
            return <Outlet />;
        }

        return null;
    }
};
