import { ExportOutlined } from '@ant-design/icons';
import { Button, Flex, Tag, Typography } from 'antd';
import { formatDistanceToNow } from 'date-fns';
import { useTranslation } from 'react-i18next';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { useGetLatestDataQualitySummaryForOutputPortQuery } from '@/store/api/services/generated/outputPortDataQualityApi.ts';
import { formatQualityStatus, getQualityStatusColor, getQualityStatusIcon } from '@/utils/quality-status.helper';

interface Props {
    dataProductId: string;
    datasetId: string;
}

export function DatasetQuality({ dataProductId, datasetId }: Props) {
    const { t } = useTranslation();
    const { data: summary, isLoading } = useGetLatestDataQualitySummaryForOutputPortQuery({
        dataProductId,
        id: datasetId,
    });

    if (isLoading) return null;

    return (
        <Flex vertical gap="small">
            <Typography.Title level={5}>{t('Quality Status')}</Typography.Title>
            {summary ? (
                <Flex vertical gap="small" align="flex-start">
                    <Tag
                        icon={<CustomSvgIconLoader iconComponent={getQualityStatusIcon(summary.overall_status)} />}
                        color={getQualityStatusColor(summary.overall_status)}
                        variant={'outlined'}
                    >
                        {formatQualityStatus(summary.overall_status, t)}
                    </Tag>
                    <Typography.Text type="secondary">
                        {formatDistanceToNow(new Date(summary.created_at), { addSuffix: true })}
                    </Typography.Text>
                    {summary?.details_url && (
                        <Button
                            type="link"
                            href={summary.details_url}
                            target="_blank"
                            icon={<ExportOutlined />}
                            size="small"
                            style={{ width: 'fit-content', padding: 0 }}
                        >
                            {t('View details')}
                        </Button>
                    )}
                </Flex>
            ) : (
                <Typography.Text type="secondary">
                    {t('Ask the owners to publish data quality information')}
                </Typography.Text>
            )}
        </Flex>
    );
}
