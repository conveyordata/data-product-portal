import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataProductLifeCycle } from '@/store/api/services/generated/dataProductsApi.ts';
import type { TagModel } from '@/types/tag';
import styles from './data-product-description.module.scss';

type Props = {
    lifecycle: DataProductLifeCycle | null;
    type: string;
    description: string;
    domain: string;
    tags: TagModel[];
    namespace: string;
};

export function DataProductDescription({ lifecycle, type, description, domain, tags, namespace }: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical className={styles.statusInfo}>
            <Space className={styles.contentSubtitle}>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Tag color={lifecycle?.color ?? 'default'}>{lifecycle?.name ?? t('Unknown')}</Tag>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Domain')}</Typography.Text>
                    <Typography.Text>{domain}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Type')}</Typography.Text>
                    <Typography.Text>{type}</Typography.Text>
                </Flex>
            </Space>
            <Space size={'small'}>
                {tags.map((tag) => (
                    <Tag color={tag.rolled_up ? 'red' : 'success'} key={tag.id}>
                        {tag.value}
                    </Tag>
                ))}
            </Space>
            <Space>
                <Typography.Paragraph italic>{description}</Typography.Paragraph>
            </Space>
        </Flex>
    );
}
