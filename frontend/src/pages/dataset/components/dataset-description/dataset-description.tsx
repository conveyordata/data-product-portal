import styles from './dataset-description.module.scss';
import { Badge, Flex, Space, Tag, Typography } from 'antd';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { useTranslation } from 'react-i18next';
import { DatasetStatus } from '@/types/dataset/dataset.contract.ts';
import { TagModel } from '@/types/tag';

type Props = {
    status: DatasetStatus;
    accessType?: string;
    description: string;
    businessArea: string;
    tags: TagModel[];
};

export function DatasetDescription({ status, accessType, description, businessArea, tags }: Props) {
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
            <Flex>
                {tags.map( tag => (
                        <Tag color='success'>
                            {tag.value}
                        </Tag>
                ))}
            </Flex>
            <Space>
                <Typography.Text italic>{description}</Typography.Text>
            </Space>
        </Flex>
    );
}
