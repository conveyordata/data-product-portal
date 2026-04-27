import { Tag, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';

import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import type { FreshnessStatus } from '@/store/api/services/generated/dataProductsOutputPortsApi';
import {
    formatFreshnessStatus,
    getFreshnessStatusColor,
    getFreshnessStatusIcon,
} from '@/utils/freshness-status.helper';

interface Props {
    status: FreshnessStatus;
    deadlineTime?: string | null;
}

export function FreshnessBadge({ status, deadlineTime }: Props) {
    const { t } = useTranslation();
    const tooltipTitle = deadlineTime
        ? t('Expected to refresh daily before {{time}} UTC', { time: deadlineTime })
        : undefined;

    return (
        <Tooltip title={tooltipTitle}>
            <Tag
                color={getFreshnessStatusColor(status)}
                icon={<CustomSvgIconLoader iconComponent={getFreshnessStatusIcon(status)} />}
                variant={'outlined'}
            >
                {formatFreshnessStatus(status, t)}
            </Tag>
        </Tooltip>
    );
}
