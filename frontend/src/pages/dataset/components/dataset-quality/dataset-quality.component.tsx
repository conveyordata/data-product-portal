import { Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { QualityBadge } from '@/components/quality-badge/quality-badge.component';
import { useGetLatestDataQualitySummaryForOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsDataQualityApi.ts';

const { Title, Text } = Typography;

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
            <Title level={5}>{t('Quality Status')}</Title>
            {summary ? (
                <Flex vertical gap="small" align="flex-start">
                    <QualityBadge
                        quality_status={summary.overall_status}
                        createdAt={summary.created_at}
                        detailsUrl={summary.details_url ?? undefined}
                    />
                </Flex>
            ) : (
                <Text type="secondary">{t('Ask the owners to publish data quality information')}</Text>
            )}
        </Flex>
    );
}
