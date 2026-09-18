import type { TFunction } from 'i18next';

import { DataProductVisibility } from '@/store/api/services/generated/dataProductsApi.ts';

export const getDataProductVisibilityLabel = (t: TFunction, visibility: DataProductVisibility) => {
    switch (visibility) {
        case DataProductVisibility.Hidden:
            return t('Hidden');
        case DataProductVisibility.Discoverable:
            return t('Discoverable');
        default:
            return t('Unknown');
    }
};
