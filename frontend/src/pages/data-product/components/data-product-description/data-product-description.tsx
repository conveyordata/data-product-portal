import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import styles from './data-product-description.module.scss';
import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    lifecycle: DataProductLifeCycleContract;
    type: string;
    description: string;
    businessArea: string;
};

export function DataProductDescription({ lifecycle, type, description, businessArea }: Props) {
    const { t } = useTranslation();

    return (
        <>
            <Flex vertical className={styles.statusInfo}>
                <Space className={styles.contentSubtitle}>
                    <Flex className={styles.statusBadge}>
                        <Typography.Text strong>{t('Status')}</Typography.Text>
                        <Tag color={lifecycle.color}>{lifecycle.name}</Tag>
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
