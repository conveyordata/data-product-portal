import axios, { type AxiosResponse } from 'axios';
import type { ApiError } from '@/store/common/api-result.ts';
import { dispatchNotification, type NotificationOptions } from '@/utils/feedback.ts';

export function getApiErrorDetail(error: unknown): string | undefined {
    if (!error || typeof error !== 'object') {
        return undefined;
    }

    const mutationError = error as ApiError & { data?: ApiError; detail?: unknown };
    // Checks both nested data.detail and top-level detail
    const detail = mutationError.data?.detail ?? mutationError.detail;

    if (typeof detail === 'string') {
        return detail;
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map((err) => {
                const msg = err?.msg;
                if (typeof msg === 'string') {
                    // Strip "Value error, " prefix from pydantic validation messages
                    return msg.replace(/^Value error,\s*/i, '');
                }
                return null;
            })
            .filter(Boolean);

        if (messages.length > 0) {
            return messages.join(', ');
        }
    }

    return undefined;
}

export const defaultErrorMessage: NotificationOptions = {
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

export function showGenericErrorMessage(error: unknown): void {
    if (axios.isAxiosError<ApiError>(error) && error.response) {
        showErrorMessageToast(error.response);
        return;
    }
    dispatchNotification(defaultErrorMessage);
}
