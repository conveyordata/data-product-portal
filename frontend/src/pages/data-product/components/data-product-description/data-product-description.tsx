import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import styles from './data-product-description.module.scss';
import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { TagModel } from '@/types/tag';

type Props = {
    lifecycle: DataProductLifeCycleContract;
    type: string;
    description: string;
    businessArea: string;
    tags: TagModel[];
};

export function DataProductDescription({ lifecycle, type, description, businessArea, tags }: Props) {
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
                <Flex>
                    {tags.map((tag) => (
                        <Tag color="success">{tag.value}</Tag>
                    ))}
                </Flex>
                <Space>
                    <Typography.Paragraph italic>{description}</Typography.Paragraph>
                </Space>
            </Flex>
        </>
    );
}
