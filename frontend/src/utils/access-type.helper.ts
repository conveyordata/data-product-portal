import { DatasetAccess } from '@/types/dataset';
import i18n from '@/i18n.ts';

export const getDatasetAccessTypeLabel = (accessType: DatasetAccess) => {
    switch (accessType) {
        case DatasetAccess.Public:
            return i18n.t('Public');
        case DatasetAccess.Restricted:
            return i18n.t('Restricted');
        default:
            return i18n.t('Unknown');
    }
};
