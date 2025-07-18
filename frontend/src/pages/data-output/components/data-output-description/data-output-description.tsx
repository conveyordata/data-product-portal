import { Badge, Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import type { DataOutputStatus } from '@/types/data-output';
import type { TagModel } from '@/types/tag';
import { getDataOutputType } from '@/utils/data-output-type.helper';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';

import styles from './data-output-description.module.scss';

type Props = {
    status: DataOutputStatus;
    type: string;
    description: string;
    tags: TagModel[];
    namespace: string;
};

export function DataOutputDescription({ status, type, description, tags, namespace }: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical className={styles.statusInfo}>
            <Space className={styles.contentSubtitle}>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Badge
                        status={getBadgeStatus(status)}
                        text={getStatusLabel(t, status)}
                        className={styles.noSelect}
                    />
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Type')}</Typography.Text>
                    <Typography.Text>{getDataOutputType(type, t)}</Typography.Text>
                </Flex>
            </Space>
            <Flex>
                {tags.map((tag) => (
                    <Tag color="success" key={tag.id}>
                        {tag.value}
                    </Tag>
                ))}
            </Flex>
            <Space>
                <Typography.Paragraph italic>{description}</Typography.Paragraph>
            </Space>
        </Flex>
    );
}
