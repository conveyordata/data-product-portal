import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataProductContract } from '@/types/data-product';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import type { TagModel } from '@/types/tag';
import styles from './dataset-description.module.scss';

type Props = {
    lifecycle: DataProductLifeCycleContract;
    accessType?: string;
    description: string;
    data_product: DataProductContract;
    domain: string;
    tags: TagModel[];
    namespace: string;
};

export function DatasetDescription({
    lifecycle,
    accessType,
    description,
    data_product,
    domain,
    tags,
    namespace,
}: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical className={styles.statusInfo}>
            <Space className={styles.contentSubtitle}>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Tag color={lifecycle.color}>{lifecycle.name}</Tag>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Data Product')}</Typography.Text>
                    <Typography.Text>{data_product.name}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Domain')}</Typography.Text>
                    <Typography.Text>{domain}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Access Type')}</Typography.Text>
                    <Typography.Text>{accessType}</Typography.Text>
                </Flex>
            </Space>
            <Flex>
                {tags.map((tag) => (
                    <Tag color={tag.rolled_up ? 'red' : 'success'} key={tag.id}>
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
