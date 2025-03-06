import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { TagModel } from '@/types/tag';

import styles from './data-product-description.module.scss';

type Props = {
    lifecycle: DataProductLifeCycleContract;
    type: string;
    description: string;
    domain: string;
    tags: TagModel[];
};

export function DataProductDescription({ lifecycle, type, description, domain, tags }: Props) {
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
                        <Typography.Text strong>{t('Domain')}</Typography.Text>
                        <Typography.Text>{domain}</Typography.Text>
                    </Flex>
                    <Flex className={styles.statusBadge}>
                        <Typography.Text strong>{t('Type')}</Typography.Text>
                        <Typography.Text>{type}</Typography.Text>
                    </Flex>
                </Space>
                <Flex>
                    {tags.map((tag) => (
                        <Tag color={tag.rolled_up ? 'red' : 'success'}>{tag.value}</Tag>
                    ))}
                </Flex>
                <Space>
                    <Typography.Paragraph italic>{description}</Typography.Paragraph>
                </Space>
            </Flex>
        </>
    );
}
