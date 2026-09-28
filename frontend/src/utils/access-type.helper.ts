import type { TFunction } from 'i18next';

import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';

const ACCESS_FUNCTION_ORDER = [
    OutputPortAccessType.Unrestricted,
    OutputPortAccessType.Restricted,
    OutputPortAccessType.Private,
];

export const compareAccessFunctions = (a: OutputPortAccessType, b: OutputPortAccessType) =>
    ACCESS_FUNCTION_ORDER.indexOf(a) - ACCESS_FUNCTION_ORDER.indexOf(b);

export const isAllowedForDataProduct = (accessType: OutputPortAccessType, hiddenDataProduct: boolean) =>
    !hiddenDataProduct || accessType === OutputPortAccessType.Private;

export const getAccessFunctionLabel = (t: TFunction, accessType: OutputPortAccessType) => {
    switch (accessType) {
        case OutputPortAccessType.Unrestricted:
            return t('Auto-approve');
        case OutputPortAccessType.Restricted:
            return t('Approval required');
        case OutputPortAccessType.Private:
            return t('Invite only (hidden)');
        default:
            return accessType satisfies never;
    }
};
