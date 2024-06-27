import styles from './data-product-description.module.scss';
import { Badge, Flex, Space, Typography } from 'antd';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { useTranslation } from 'react-i18next';
import { DataProductStatus } from '@/types/data-product';

type Props = {
    status: DataProductStatus;
    type: string;
    description: string;
    businessArea: string;
};

export function DataProductDescription({ status, type, description, businessArea }: Props) {
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
                        <Typography.Text strong>{t('Business Area')}</Typography.Text>
                        <Typography.Text>{businessArea}</Typography.Text>
                    </Flex>
                    <Flex className={styles.statusBadge}>
                        <Typography.Text strong>{t('Type')}</Typography.Text>
                        <Typography.Text>{type}</Typography.Text>
                    </Flex>
                </Space>
                <Space>
                    <Typography.Paragraph italic>{description}</Typography.Paragraph>
                </Space>
            </Flex>
        </>
    );
}
