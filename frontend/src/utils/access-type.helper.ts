import { DatasetAccess } from '@/types/dataset';
import type { TFunction } from 'i18next';

export const getDatasetAccessTypeLabel = (t: TFunction, accessType: DatasetAccess) => {
    switch (accessType) {
        case DatasetAccess.Public:
            return t('Public');
        case DatasetAccess.Restricted:
            return t('Restricted');
        default:
            return t('Unknown');
    }
};
