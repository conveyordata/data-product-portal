import styles from './data-output-description.module.scss';
import { Badge, Flex, Space, Typography } from 'antd';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { useTranslation } from 'react-i18next';
import { DataOutputStatus } from '@/types/data-output';
import { getDataOutputType } from '@/utils/data-output-type.helper';

type Props = {
    status: DataOutputStatus;
    type: string;
    description: string;
};

export function DataOutputDescription({ status, type, description }: Props) {
    const { t } = useTranslation();

    return (
        <>
            <Flex vertical className={styles.statusInfo}>
                <Space className={styles.contentSubtitle}>
                    <Flex className={styles.statusBadge}>
                        <Typography.Text strong>{t('Status')}</Typography.Text>
                        <Badge
                            status={getBadgeStatus(status)}
                            text={getStatusLabel(status)}
                            className={styles.noSelect}
                        />
                    </Flex>
                    <Flex className={styles.statusBadge}>
                        <Typography.Text strong>{t('Type')}</Typography.Text>
                        <Typography.Text>{getDataOutputType(type, t)}</Typography.Text>
                    </Flex>
                </Space>
                <Space>
                    <Typography.Paragraph italic>{description}</Typography.Paragraph>
                </Space>
            </Flex>
        </>
    );
}
