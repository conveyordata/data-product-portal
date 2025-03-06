import chartAnalytics from '@/assets/icons/chart-analytics-icon.svg?react';
import chartPieIcon from '@/assets/icons/chart-pie-icon.svg?react';
import chipIcon from '@/assets/icons/chip-icon.svg?react';
import explorationIcon from '@/assets/icons/exploration-icon.svg?react';
import ingestionIcon from '@/assets/icons/ingestion-icon.svg?react';
import robotIcon from '@/assets/icons/robot-icon.svg?react';
import { DataProductIcon } from '@/types/data-product-type/data-product-type.contract';

export function getDataProductTypeIcon(dataProductIcon?: DataProductIcon) {
    if (!dataProductIcon) return chipIcon;

    switch (dataProductIcon) {
        case DataProductIcon.Reporting:
            return chartPieIcon;
        case DataProductIcon.Processing:
            return chipIcon;
        case DataProductIcon.Exploration:
            return explorationIcon;
        case DataProductIcon.Analytics:
            return chartAnalytics;
        case DataProductIcon.MachineLearning:
            return robotIcon;
        case DataProductIcon.Ingestion:
            return ingestionIcon;
        case DataProductIcon.Default:
            return chipIcon;
        default:
            return chipIcon;
    }
}
