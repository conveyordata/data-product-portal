import type { BaseQueryFn } from '@reduxjs/toolkit/query';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import axios from 'axios';
import { User } from 'oidc-client-ts';

import { AppConfig } from '@/config/app-config.ts';
import type { ApiError } from '@/store/common/api-result.ts';
import { dispatchNotification, type NotificationOptions } from '@/utils/feedback.ts';

type AxiosBaseQueryExtraOptions = {
    suppressErrorToast?: boolean;
};

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

const defaultErrorMessage: NotificationOptions = {
    title: 'Something went wrong',
    description: 'Please try again later',
    type: 'error',
};

function showErrorMessageToast(err: AxiosResponse<ApiError>) {
    const { correlation_id: correlationId = defaultErrorMessage.title, detail = defaultErrorMessage.description } =
        err.data;

    const title = typeof detail === 'string' ? detail : defaultErrorMessage.title;

    dispatchNotification({
        title,
        description: correlationId,
        type: 'error',
    });
}

export const axiosBaseQuery =
    (
        { baseUrl }: { baseUrl: string } = { baseUrl: AppConfig.getApiBaseURL() },
    ): BaseQueryFn<
        {
            url: string;
            method?: AxiosRequestConfig['method'];
            data?: AxiosRequestConfig['data'];
            body?: AxiosRequestConfig['data'];
            params?: Record<string, string | number | boolean | undefined | null>;
            headers?: { [key: string]: string | number };
        },
        unknown,
        unknown,
        AxiosBaseQueryExtraOptions
    > =>
    async ({ url, method, data, body, params, headers }, api, extraOptions) => {
        try {
            const user = getUser();
            const result = await axios({
                url: baseUrl + url,
                method,
                data: data ?? body,
                params,
                signal: api.signal,
                headers: {
                    ...headers,
                    ...(user?.access_token && { Authorization: `${user.token_type} ${user.access_token}` }),
                },
            });
            return { data: result.data };
        } catch (axiosError: unknown) {
            if (axios.isAxiosError<ApiError>(axiosError) && axiosError.response) {
                if (!extraOptions.suppressErrorToast) {
                    showErrorMessageToast(axiosError.response);
                }

                return { error: axiosError.response.data };
            }

            dispatchNotification(defaultErrorMessage);

            return { error: { correlation_id: 'NA', detail: defaultErrorMessage.description } };
        }
    };
