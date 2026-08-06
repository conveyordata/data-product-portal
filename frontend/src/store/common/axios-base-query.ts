import type { BaseQueryFn } from '@reduxjs/toolkit/query';
import type { AxiosError, AxiosRequestConfig } from 'axios';
import axios, { type AxiosResponse } from 'axios';
import { User } from 'oidc-client-ts';

import { AppConfig } from '@/config/app-config.ts';
import type { ApiError } from '@/types/api-result.ts';
import { dispatchNotification, type NotificationOptions } from '@/utils/feedback.ts';

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

function shouldShowErrorToast(status: number, url: string) {
    if (status === 404) {
        if (url.includes('data_quality_summary')) {
            return false;
        }
    }
    return true;
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
        unknown
    > =>
    async ({ url, method, data, body, params, headers }) => {
        try {
            const user = getUser();
            const result = await axios({
                url: baseUrl + url,
                method,
                data: data ?? body,
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
                if (shouldShowErrorToast(err.response.status, url)) {
                    showErrorMessageToast(err.response);
                }
            } else {
                dispatchNotification(defaultErrorMessage);
            }

            return { error: { correlation_id: 'NA', detail: defaultErrorMessage.description } };
        }
    };
