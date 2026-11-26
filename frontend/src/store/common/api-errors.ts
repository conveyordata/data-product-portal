import { getApiErrorDetail } from '@/store/common/errors.ts';

export const INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL =
    'Access modes of technical asset are incompatible with access modes of output port';
export const TECHNICAL_ASSET_NOT_SHAREABLE_ERROR_DETAIL =
    'Technical assets of this type are not shareable and cannot be linked to an Output Port';
export function isTechnicalAssetNotShareableError(error: unknown): boolean {
    return getApiErrorDetail(error) === TECHNICAL_ASSET_NOT_SHAREABLE_ERROR_DETAIL;
}

export function isIncompatibleAccessModesError(error: unknown): boolean {
    return getApiErrorDetail(error) === INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL;
}
