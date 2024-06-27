import type { BaseQueryFn } from '@reduxjs/toolkit/query';
import type { AxiosError, AxiosRequestConfig } from 'axios';
import axios, { AxiosResponse } from 'axios';
import { AppConfig } from '@/config/app-config.ts';
import { ApiError } from '@/types/api-result.ts';
import { NotificationState, showNotification } from '@/store/features/feedback/feedback-slice.ts';
import { Headers, QueryParams } from '@/types/http.ts';
import { User } from 'oidc-client-ts';
import i18n from '@/i18n.ts';

interface CustomAxiosError extends AxiosError {
    response?: AxiosResponse<ApiError>;
}

function getUser() {
    const skipAuth = AppConfig.isOidcDisabled();
    if (skipAuth) {
        return null;
    }
    const { authority, client_id } = AppConfig.getOidcCredentials();
    const oidcStorage = sessionStorage.getItem(`oidc.user:${authority}:${client_id}`);
    if (!oidcStorage) {
        return null;
    }

    return User.fromStorageString(oidcStorage);
}

export const axiosBaseQuery =
    (
        {
            baseUrl,
        }: {
            baseUrl: string;
        } = { baseUrl: AppConfig.getApiBaseURL() },
    ): BaseQueryFn<
        {
            url: string;
            method?: AxiosRequestConfig['method'];
            data?: AxiosRequestConfig['data'];
            params?: QueryParams;
            headers?: Headers;
        },
        unknown,
        unknown
    > =>
    async ({ url, method, data, params, headers }, api) => {
        const defaultErrorMessage: NotificationState = {
            message: i18n.t('Something went wrong'),
            description: i18n.t('Please try again later'),
            type: 'error',
        };

        try {
            const user = getUser();
            const result = await axios({
                url: baseUrl + url,
                method,
                data,
                params,
                headers: {
                    ...headers,
                    ...(user && user.access_token && { Authorization: `${user.token_type} ${user.access_token}` }),
                },
            });
            return { data: result.data };
        } catch (axiosError: unknown) {
            const err = axiosError as CustomAxiosError;

            if (err.response) {
                const {
                    correlation_id: correlationId = defaultErrorMessage.message,
                    detail = defaultErrorMessage.description,
                } = err.response.data;

                const message = typeof detail === 'string' ? detail : defaultErrorMessage.message;

                api.dispatch(
                    showNotification({
                        message,
                        description: correlationId,
                        type: 'error',
                    }),
                );
            } else {
                api.dispatch(showNotification(defaultErrorMessage));
            }

            return { error: { correlation_id: 'NA', detail: defaultErrorMessage.description } };
        }
    };
