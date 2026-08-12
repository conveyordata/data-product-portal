import type { BaseQueryFn } from '@reduxjs/toolkit/query';
import type { AxiosRequestConfig } from 'axios';
import axios from 'axios';
import { User } from 'oidc-client-ts';

import { AppConfig } from '@/config/app-config.ts';
import type { ApiError } from '@/store/common/api-result.ts';
import { defaultErrorMessage, showGenericErrorMessage } from '@/store/common/errors.ts';

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
            if (!extraOptions?.suppressErrorToast) {
                showGenericErrorMessage(axiosError);
            }
            if (axios.isAxiosError<ApiError>(axiosError) && axiosError.response) {
                return { error: axiosError.response.data };
            }
            return { error: { correlation_id: 'NA', detail: defaultErrorMessage.description } };
        }
    };
