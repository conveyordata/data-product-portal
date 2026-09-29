import type { TFunction } from 'i18next';

import { OutputPortAccessFunction } from '@/store/api/services/generated/dataProductsApi.ts';

export const ACCESS_FUNCTION_ORDER = [
    OutputPortAccessFunction.Unrestricted,
    OutputPortAccessFunction.Restricted,
    OutputPortAccessFunction.Private,
];

export const compareAccessFunctions = (a: OutputPortAccessFunction, b: OutputPortAccessFunction) =>
    ACCESS_FUNCTION_ORDER.indexOf(a) - ACCESS_FUNCTION_ORDER.indexOf(b);

export const fitsDataProductVisibility = (accessFunction: OutputPortAccessFunction, hiddenDataProduct: boolean) =>
    !hiddenDataProduct || accessFunction === OutputPortAccessFunction.Private;

export const getAccessFunctionLabel = (t: TFunction, accessFunction: OutputPortAccessFunction) => {
    switch (accessFunction) {
        case OutputPortAccessFunction.Unrestricted:
            return t('Auto-approve');
        case OutputPortAccessFunction.Restricted:
            return t('Approval required');
        case OutputPortAccessFunction.Private:
            return t('Invite only (hidden)');
        default:
            return accessFunction satisfies never;
    }
};
