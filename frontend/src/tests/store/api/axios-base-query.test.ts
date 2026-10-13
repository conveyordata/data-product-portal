import type { BaseQueryApi } from '@reduxjs/toolkit/query';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { axiosBaseQuery } from '@/store/common/axios-base-query.ts';
import { server } from '@/tests/mocks/server.ts';
import { registerFeedbackApi, unregisterFeedbackApi } from '@/utils/feedback.ts';

const baseUrl = window.location.origin;

const notification = {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    open: vi.fn(),
    destroy: vi.fn(),
};

const message = {
    info: vi.fn(),
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    loading: vi.fn(),
    open: vi.fn(),
    destroy: vi.fn(),
};

function createBaseQueryApi(signal = new AbortController().signal): BaseQueryApi {
    return {
        signal,
        abort: vi.fn(),
        dispatch: vi.fn(),
        endpoint: 'testEndpoint',
        extra: undefined,
        forced: false,
        getState: vi.fn(),
        type: 'query',
    };
}

describe('axiosBaseQuery', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        registerFeedbackApi({ message, notification });
    });

    afterEach(() => {
        unregisterFeedbackApi();
    });

    it('passes the RTK Query abort signal to axios', async () => {
        const query = axiosBaseQuery({ baseUrl });
        const controller = new AbortController();
        const handler = vi.fn(() => HttpResponse.json({ ok: true }));
        server.use(http.get(`${baseUrl}/resource`, handler));
        controller.abort();

        await query({ url: '/resource' }, createBaseQueryApi(controller.signal), {});

        expect(handler).not.toHaveBeenCalled();
    });

    it('adds the active user header from localStorage when available', async () => {
        const query = axiosBaseQuery({ baseUrl });
        let activeUserHeader: string | null = null;
        server.use(
            http.get(`${baseUrl}/resource`, ({ request }) => {
                activeUserHeader = request.headers.get('X-user');
                return HttpResponse.json({ ok: true });
            }),
        );
        localStorage.setItem('activeUserHeader', 'user-123');

        await query({ url: '/resource' }, createBaseQueryApi(), {});

        expect(activeUserHeader).toBe('user-123');
    });

    it('shows the error toast when extraOptions is undefined', async () => {
        const query = axiosBaseQuery({ baseUrl });
        server.use(http.get(`${baseUrl}/resource`, () => HttpResponse.error()));

        await query({ url: '/resource' }, createBaseQueryApi(), undefined as never);

        expect(notification.error).toHaveBeenCalled();
    });

    it('falls back cleanly for network errors', async () => {
        const query = axiosBaseQuery({ baseUrl });
        server.use(http.get(`${baseUrl}/resource`, () => HttpResponse.error()));

        await expect(query({ url: '/resource' }, createBaseQueryApi(), {})).resolves.toEqual({
            error: {
                correlation_id: 'NA',
                detail: 'Please try again later',
            },
        });
        expect(notification.error).toHaveBeenCalledWith({
            title: 'Something went wrong',
            description: 'Please try again later',
            duration: false,
        });
    });

    it('suppresses the error toast when requested through extraOptions', async () => {
        const query = axiosBaseQuery({ baseUrl });
        const body = {
            correlation_id: 'corr-123',
            detail: 'Request failed',
        };
        server.use(http.get(`${baseUrl}/resource`, () => HttpResponse.json(body, { status: 400 })));

        await expect(query({ url: '/resource' }, createBaseQueryApi(), { suppressErrorToast: true })).resolves.toEqual({
            error: body,
        });
        expect(notification.error).not.toHaveBeenCalled();
    });

    it('passes FormData bodies through unchanged', async () => {
        const query = axiosBaseQuery({ baseUrl });
        let uploadedText: string | null = null;
        server.use(
            http.post(`${baseUrl}/upload`, async ({ request }) => {
                const uploadedFile = (await request.formData()).get('file');
                uploadedText = uploadedFile && typeof uploadedFile !== 'string' ? await uploadedFile.text() : null;
                return HttpResponse.json({ ok: true });
            }),
        );
        const formData = new FormData();
        formData.append('file', new Blob(['schema: []'], { type: 'application/yaml' }));

        await query({ url: '/upload', method: 'POST', body: formData }, createBaseQueryApi(), {});

        expect(uploadedText).toBe('schema: []');
    });
});
