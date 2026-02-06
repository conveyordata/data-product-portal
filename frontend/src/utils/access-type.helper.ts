import type { TFunction } from 'i18next';

import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';

export const getDatasetAccessTypeLabel = (t: TFunction, accessType: OutputPortAccessType) => {
    switch (accessType) {
        case OutputPortAccessType.Public:
            return t('Public');
        case OutputPortAccessType.Restricted:
            return t('Restricted');
        case OutputPortAccessType.Private:
            return t('Private');
        default:
            return t('Unknown');
    }
};
