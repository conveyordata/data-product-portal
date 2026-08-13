import { getApiErrorDetail } from '@/store/common/errors.ts';

export const INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL =
    'Access modes of technical asset are incompatible with access modes of output port';
export const CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR =
    'Cannot remove the specified technical asset types because they are in use by technical assets or input port requests.';

export function isIncompatibleAccessModesError(error: unknown): boolean {
    return getApiErrorDetail(error) === INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL;
}

export function isCanNotRemoveTechnicalAssetTypesError(error: unknown): boolean {
    return getApiErrorDetail(error) === CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR;
}
