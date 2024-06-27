import { DataProductIcon } from '@/types/data-product-type';
import chartAnalytics from '@/assets/icons/chart-analytics-icon.svg?react';
import chipIcon from '@/assets/icons/chip-icon.svg?react';
import robotIcon from '@/assets/icons/robot-icon.svg?react';
import explorationIcon from '@/assets/icons/exploration-icon.svg?react';
import chartPieIcon from '@/assets/icons/chart-pie-icon.svg?react';
import ingestionIcon from '@/assets/icons/ingestion-icon.svg?react';

export function getDataProductTypeIcon(dataProductIcon?: DataProductIcon) {
    if (!dataProductIcon) return chipIcon;

    switch (dataProductIcon) {
        case 'reporting':
            return chartPieIcon;
        case 'processing':
            return chipIcon;
        case 'exploration':
            return explorationIcon;
        case 'analytics':
            return chartAnalytics;
        case 'machine_learning':
            return robotIcon;
        case 'ingestion':
            return ingestionIcon;
        case 'default':
            return chipIcon;
        default:
            return chipIcon;
    }
}
