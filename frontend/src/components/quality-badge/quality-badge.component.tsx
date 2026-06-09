import { ExportOutlined } from '@ant-design/icons';
import { Flex, Space, Tag, Tooltip, Typography } from 'antd';
import { formatDistanceToNow } from 'date-fns';
import { useTranslation } from 'react-i18next';
import type { DataQualityStatus } from '@/store/api/services/generated/dataProductsOutputPortsDataQualityApi';
import { formatQualityStatus, getQualityStatusColor, getQualityStatusIcon } from '@/utils/quality-status.helper.tsx';

const { Text } = Typography;

type QualityBadgeProps = {
    quality_status: DataQualityStatus;
    createdAt?: string;
    detailsUrl?: string;
};

export function QualityBadge({ quality_status, createdAt, detailsUrl }: QualityBadgeProps) {
    const { t } = useTranslation();

    const icon = getQualityStatusIcon(quality_status);
    const color = getQualityStatusColor(quality_status);

    const tag = (
        <Tag color={color} variant="outlined" style={{ padding: '4px 10px', minWidth: '9em' }}>
            <Flex align="center" vertical>
                <Flex align="center" justify="space-between" style={{ width: '100%' }}>
                    <Space size={4} align="baseline">
                        {icon}
                        <Text strong style={{ color: 'inherit' }}>
                            {formatQualityStatus(quality_status, t)}
                        </Text>
                    </Space>
                    {detailsUrl ? (
                        <Tooltip title={t('View details')}>
                            <ExportOutlined style={{ fontSize: 11, opacity: 0.7, paddingLeft: '1em' }} />
                        </Tooltip>
                    ) : null}
                </Flex>

                {createdAt ? (
                    <Text style={{ fontSize: 12, color: 'inherit', opacity: 0.8, margin: '0 4px' }}>
                        {formatDistanceToNow(new Date(createdAt), { addSuffix: true })}
                    </Text>
                ) : null}
            </Flex>
        </Tag>
    );

    if (createdAt === undefined) {
        return tag;
    }

    return (
        <a
            href={detailsUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'inline-block', textDecoration: 'none' }}
        >
            {tag}
        </a>
    );
}
