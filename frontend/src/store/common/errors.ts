import axios, { type AxiosResponse } from 'axios';
import type { ApiError } from '@/store/common/api-result.ts';
import { dispatchNotification, type NotificationOptions } from '@/utils/feedback.ts';

export const INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL =
    'Access modes of technical asset are incompatible with access modes of output port';
export const CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR =
    'Cannot remove the specified technical asset types because they are in use by technical assets or input port requests.';
export function getApiErrorDetail(error: unknown): string | undefined {
    if (!error || typeof error !== 'object') {
        return undefined;
    }

    const mutationError = error as ApiError & { data?: ApiError };
    const detail = mutationError.data?.detail ?? mutationError.detail;
    return typeof detail === 'string' ? detail : undefined;
}

export function isIncompatibleAccessModesError(error: unknown): boolean {
    return getApiErrorDetail(error) === INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL;
}

export function isCanNotRemoveTechnicalAssetTypesError(error: unknown): boolean {
    return getApiErrorDetail(error) === CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR;
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
