import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { TagModel } from '@/types/tag';

type Props = {
    type: string;
    description: string;
    domain: string;
    tags: TagModel[];
    namespace: string;
};

export function DataProductDescription({ type, description, domain, tags, namespace }: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical gap="middle">
            <Space size="large">
                <Flex gap="small">
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Flex>
                <Flex gap="small">
                    <Typography.Text strong>{t('Domain')}</Typography.Text>
                    <Typography.Text>{domain}</Typography.Text>
                </Flex>
                <Flex gap="small">
                    <Typography.Text strong>{t('Type')}</Typography.Text>
                    <Typography.Text>{type}</Typography.Text>
                </Flex>
            </Space>
            <Space size="small">
                {tags.map((tag) => (
                    <Tag color={tag.rolled_up ? 'red' : 'success'} key={tag.id}>
                        {tag.value}
                    </Tag>
                ))}
            </Space>
            <Typography.Paragraph italic>{description}</Typography.Paragraph>
        </Flex>
    );
}
