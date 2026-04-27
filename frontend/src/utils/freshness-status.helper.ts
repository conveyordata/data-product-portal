import { ClockCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import type { TFunction } from 'i18next';

import { FreshnessStatus } from '@/store/api/services/generated/dataProductsOutputPortsApi';

export const getFreshnessStatusIcon = (status: FreshnessStatus) => {
    switch (status) {
        case FreshnessStatus.Fresh:
            return ClockCircleOutlined;
        case FreshnessStatus.Stale:
            return ClockCircleOutlined;
        default:
            return QuestionCircleOutlined;
    }
};

export const getFreshnessStatusColor = (status: FreshnessStatus): string => {
    switch (status) {
        case FreshnessStatus.Fresh:
            return 'success';
        case FreshnessStatus.Stale:
            return 'error';
        default:
            return 'default';
    }
};

export const formatFreshnessStatus = (status: FreshnessStatus, t: TFunction): string => {
    switch (status) {
        case FreshnessStatus.Fresh:
            return t('Fresh');
        case FreshnessStatus.Stale:
            return t('Stale');
        default:
            return t('Unknown');
    }
};
