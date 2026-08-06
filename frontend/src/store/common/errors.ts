import type { ApiError } from '@/store/common/api-result.ts';

export const INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL =
    'Access modes of technical asset are incompatible with access modes of output port';

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
