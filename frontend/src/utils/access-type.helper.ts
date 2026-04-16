import type { TFunction } from 'i18next';

import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';

export const getDatasetAccessTypeLabel = (t: TFunction, accessType: OutputPortAccessType) => {
    switch (accessType) {
        // Backwards-compatibility
        case OutputPortAccessType.Public:
            return t('Unrestricted');
        case OutputPortAccessType.Unrestricted:
            return t('Unrestricted');
        case OutputPortAccessType.Restricted:
            return t('Restricted');
        case OutputPortAccessType.Private:
            return t('Private');
        default:
            return t('Unknown');
    }
};
