import { getApiErrorDetail } from '@/store/common/errors.ts';

export const INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL =
    'Access modes of technical asset are incompatible with access modes of output port';
export const CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR =
    'Cannot remove the specified technical asset types because they are in use by technical assets or input port requests.';
export const CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR =
    'Cannot remove the specified access mode because it is in use by technical assets or input port requests.';
export const TECHNICAL_ASSET_NOT_SHAREABLE_ERROR_DETAIL =
    'Technical assets of this type are not shareable and cannot be linked to an Output Port';
export function isTechnicalAssetNotShareableError(error: unknown): boolean {
    return getApiErrorDetail(error) === TECHNICAL_ASSET_NOT_SHAREABLE_ERROR_DETAIL;
}

export function isIncompatibleAccessModesError(error: unknown): boolean {
    return getApiErrorDetail(error) === INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL;
}

export function isCanNotRemoveTechnicalAssetTypesError(error: unknown): boolean {
    return getApiErrorDetail(error) === CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR;
}

export function isCanNotRemoveAccessModeInUseError(error: unknown): boolean {
    return getApiErrorDetail(error) === CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR;
}
