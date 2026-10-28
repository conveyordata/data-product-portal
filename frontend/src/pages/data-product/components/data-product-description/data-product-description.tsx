import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { EnvironmentsField } from '@/components/environments/environments-field.component.tsx';
import type { DataProductEnvironment, DataProductLifeCycle } from '@/store/api/services/generated/dataProductsApi.ts';
import type { TagModel } from '@/types/tag';

type Props = {
    lifecycle: DataProductLifeCycle | null;
    type: string;
    description: string;
    domain: string;
    tags: TagModel[];
    namespace: string;
    environments: DataProductEnvironment[];
};

export function DataProductDescription({ lifecycle, type, description, domain, tags, namespace, environments }: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical gap="middle">
            <Space size="large" wrap>
                <Flex gap="small">
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Tag color={lifecycle?.color ?? 'default'}>{lifecycle?.name ?? t('Unknown')}</Tag>
                </Flex>
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
            <EnvironmentsField environments={environments} />
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
