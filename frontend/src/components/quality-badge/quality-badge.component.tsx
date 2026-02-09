import { Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataQualityStatus } from '@/store/api/services/generated/outputPortDataQualityApi';
import { formatQualityStatus, getQualityStatusColor, getQualityStatusIcon } from '@/utils/quality-status.helper';
import { CustomSvgIconLoader } from '../icons/custom-svg-icon-loader/custom-svg-icon-loader.component';

export function QualityBadge({ quality_status }: { quality_status: DataQualityStatus }) {
    const { t } = useTranslation();
    return (
        <Tag
            color={getQualityStatusColor(quality_status)}
            icon={<CustomSvgIconLoader iconComponent={getQualityStatusIcon(quality_status)} />}
            variant={'outlined'}
        >
            {formatQualityStatus(quality_status, t)}
        </Tag>
    );
}
