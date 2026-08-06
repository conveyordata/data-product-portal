import type { BaseQueryApi } from '@reduxjs/toolkit/query';
import axios from 'axios';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { axiosBaseQuery } from '@/store/common/axios-base-query.ts';
import { dispatchNotification } from '@/utils/feedback.ts';

vi.mock('axios', () => {
    const mockAxios = vi.fn();
    return {
        default: Object.assign(mockAxios, {
            isAxiosError: vi.fn(),
        }),
    };
});

vi.mock('@/utils/feedback.ts', () => ({
    dispatchNotification: vi.fn(),
}));

function createBaseQueryApi(endpoint = 'testEndpoint'): BaseQueryApi {
    return {
        signal: new AbortController().signal,
        abort: vi.fn(),
        dispatch: vi.fn(),
        endpoint,
        extra: undefined,
        forced: false,
        getState: vi.fn(),
        type: 'query',
    };
}

describe('axiosBaseQuery', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('passes the RTK Query abort signal to axios', async () => {
        const query = axiosBaseQuery({ baseUrl: 'https://example.test' });
        const api = createBaseQueryApi();
        vi.mocked(axios).mockResolvedValueOnce({ data: { ok: true } });

        await query({ url: '/resource' }, api, {});

        expect(axios).toHaveBeenCalledWith(
            expect.objectContaining({
                signal: api.signal,
                url: 'https://example.test/resource',
            }),
        );
    });

    it('falls back cleanly for non-Axios errors', async () => {
        const query = axiosBaseQuery({ baseUrl: 'https://example.test' });
        const api = createBaseQueryApi();
        const error = new Error('boom');

        vi.mocked(axios).mockRejectedValueOnce(error);
        vi.mocked(axios.isAxiosError).mockReturnValue(false);

        await expect(query({ url: '/resource' }, api, {})).resolves.toEqual({
            error: {
                correlation_id: 'NA',
                detail: 'Please try again later',
            },
        });
        expect(dispatchNotification).toHaveBeenCalledWith({
            title: 'Something went wrong',
            description: 'Please try again later',
            type: 'error',
        });
    });

    it('suppresses the error toast when requested through extraOptions', async () => {
        const query = axiosBaseQuery({ baseUrl: 'https://example.test' });
        const api = createBaseQueryApi();
        const response = {
            data: {
                correlation_id: 'corr-123',
                detail: 'Request failed',
            },
        };

        vi.mocked(axios).mockRejectedValueOnce({ response });
        vi.mocked(axios.isAxiosError).mockReturnValue(true);

        await expect(query({ url: '/resource' }, api, { suppressErrorToast: true })).resolves.toEqual({
            error: response.data,
        });
        expect(dispatchNotification).not.toHaveBeenCalled();
    });
});
