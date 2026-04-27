import { Flex, Typography } from 'antd';
import { formatDistanceToNow } from 'date-fns';
import { useTranslation } from 'react-i18next';

import { FreshnessBadge } from '@/components/freshness-badge/freshness-badge.component';
import { useGetFreshnessSloQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi';

interface Props {
    dataProductId: string;
    datasetId: string;
}

export function DatasetFreshness({ dataProductId, datasetId }: Props) {
    const { t } = useTranslation();
    const { data: slo, isLoading } = useGetFreshnessSloQuery({
        dataProductId,
        id: datasetId,
    });

    if (isLoading) return null;
    if (!slo) return null;

    return (
        <Flex vertical gap="small">
            <Typography.Title level={5}>{t('Freshness Status')}</Typography.Title>
            <Flex vertical gap="small" align="flex-start">
                <FreshnessBadge status={slo.status} deadlineTime={slo.deadline_time} />
                {slo.last_refreshed_at && (
                    <Typography.Text type="secondary">
                        {formatDistanceToNow(new Date(slo.last_refreshed_at), { addSuffix: true })}
                    </Typography.Text>
                )}
            </Flex>
        </Flex>
    );
}
