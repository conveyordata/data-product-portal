import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    ExclamationCircleOutlined,
    ExportOutlined,
    QuestionCircleOutlined,
} from '@ant-design/icons';
import { Button, Flex, Tag, Typography } from 'antd';
import { formatDistanceToNow } from 'date-fns';
import { useTranslation } from 'react-i18next';

import {
    type DataQualityStatus,
    useGetLatestDataQualitySummaryForOutputPortQuery,
} from '@/store/api/services/generated/outputPortDataQualityApi.ts';
import styles from '../../dataset.module.scss';

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

    const getStatusIcon = (status: DataQualityStatus) => {
        switch (status) {
            case 'pass':
                return <CheckCircleOutlined />;
            case 'fail':
                return <CloseCircleOutlined />;
            case 'warn':
                return <QuestionCircleOutlined />;
            case 'error':
                return <ExclamationCircleOutlined />;
            case 'unknown':
                return <QuestionCircleOutlined />;
        }
    };

    const getStatusColor = (status: DataQualityStatus) => {
        switch (status) {
            case 'pass':
                return 'success';
            case 'fail':
                return 'error';
            case 'error':
                return 'error';
            case 'warn':
                return 'warning';
            case 'unknown':
                return 'info';
        }
    };

    function formatStatus(overall_status: DataQualityStatus) {
        switch (overall_status) {
            case 'pass':
                return 'Passed';
            case 'fail':
                return 'Failed';
            case 'error':
                return 'Error';
            case 'warn':
                return 'Warning';
            case 'unknown':
                return 'Unknown';
        }
    }

    return (
        <Flex vertical className={styles.sectionWrapper}>
            <Typography.Title level={5}>{t('Quality Status')}</Typography.Title>
            {summary ? (
                <Flex vertical gap="small" align="flex-start">
                    <Tag
                        icon={getStatusIcon(summary.overall_status)}
                        color={getStatusColor(summary.overall_status)}
                        variant={'outlined'}
                    >
                        {formatStatus(summary.overall_status)}
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
