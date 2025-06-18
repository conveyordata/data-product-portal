import type { BaseQueryFn } from '@reduxjs/toolkit/query';
import type { AxiosError, AxiosRequestConfig } from 'axios';
import axios, { type AxiosResponse } from 'axios';
import { User } from 'oidc-client-ts';

import { AppConfig } from '@/config/app-config.ts';
import { type NotificationState, showNotification } from '@/store/features/feedback/feedback-slice.ts';
import type { ApiError } from '@/types/api-result.ts';
import type { Headers, QueryParams } from '@/types/http.ts';

interface CustomAxiosError extends AxiosError {
    response?: AxiosResponse<ApiError>;
}

function getUser() {
    const skipAuth = !AppConfig.isOidcEnabled();
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
        { baseUrl }: { baseUrl: string } = { baseUrl: AppConfig.getApiBaseURL() },
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
            message: 'Something went wrong',
            description: 'Please try again later',
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
                    ...(user?.access_token && { Authorization: `${user.token_type} ${user.access_token}` }),
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
