import chartAnalytics from '@/assets/icons/chart-analytics-icon.svg?react';
import chartPieIcon from '@/assets/icons/chart-pie-icon.svg?react';
import chipIcon from '@/assets/icons/chip-icon.svg?react';
import explorationIcon from '@/assets/icons/exploration-icon.svg?react';
import ingestionIcon from '@/assets/icons/ingestion-icon.svg?react';
import robotIcon from '@/assets/icons/robot-icon.svg?react';
import { DataProductIconKey } from '@/store/api/services/generated/configurationDataProductTypesApi.ts';

export function getDataProductTypeIcon(dataProductIcon?: DataProductIconKey) {
    if (!dataProductIcon) return chipIcon;

    switch (dataProductIcon) {
        case DataProductIconKey.Reporting:
            return chartPieIcon;
        case DataProductIconKey.Processing:
            return chipIcon;
        case DataProductIconKey.Exploration:
            return explorationIcon;
        case DataProductIconKey.Analytics:
            return chartAnalytics;
        case DataProductIconKey.MachineLearning:
            return robotIcon;
        case DataProductIconKey.Ingestion:
            return ingestionIcon;
        case DataProductIconKey.Default:
            return chipIcon;
        default:
            return chipIcon;
    }
}
