import styles from './dataset-description.module.scss';
import { Badge, Flex, Space, Typography } from 'antd';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { useTranslation } from 'react-i18next';
import { DatasetStatus } from '@/types/dataset/dataset.contract.ts';

type Props = {
    status: DatasetStatus;
    accessType?: string;
    description: string;
    businessArea: string;
};

export function DatasetDescription({ status, accessType, description, businessArea }: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical className={styles.statusInfo}>
            <Space className={styles.contentSubtitle}>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Badge status={getBadgeStatus(status)} text={getStatusLabel(status)} className={styles.noSelect} />
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Business Area')}</Typography.Text>
                    <Typography.Text>{businessArea}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Access Type')}</Typography.Text>
                    <Typography.Text>{accessType}</Typography.Text>
                </Flex>
            </Space>
            <Space>
                <Typography.Text italic>{description}</Typography.Text>
            </Space>
        </Flex>
    );
}
