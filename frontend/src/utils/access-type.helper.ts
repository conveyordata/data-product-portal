import type { TFunction } from 'i18next';

import { DatasetAccess } from '@/types/dataset';

export const getDatasetAccessTypeLabel = (t: TFunction, accessType: DatasetAccess) => {
    switch (accessType) {
        case DatasetAccess.Public:
            return t('Public');
        case DatasetAccess.Restricted:
            return t('Restricted');
        case DatasetAccess.Private:
            return t('Private');
        default:
            return t('Unknown');
    }
};
