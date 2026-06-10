import { Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import type { GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
import type { DataProductLifeCycle } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { createDataProductIdPath } from '@/types/navigation';
import type { TagModel } from '@/types/tag';

type Props = {
    lifecycle: DataProductLifeCycle | null;
    accessType?: string;
    description: string;
    data_product: GetDataProductResponse;
    domain: string;
    tags: TagModel[];
    namespace: string;
};

export function OutputPortDescription({
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
        <Flex vertical gap="medium">
            <Flex wrap gap="12px 36px">
                <Space>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Tag color={lifecycle?.color ?? 'default'}>{lifecycle?.name || t('Unknown')}</Tag>
                </Space>

                <Space>
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Space>

                <Space>
                    <Typography.Text strong>{t('Data Product')}</Typography.Text>
                    <Link to={createDataProductIdPath(data_product.id)}>
                        <Typography.Text>{data_product.name}</Typography.Text>
                    </Link>
                </Space>

                <Space>
                    <Typography.Text strong>{t('Domain')}</Typography.Text>
                    <Typography.Text>{domain}</Typography.Text>
                </Space>

                {accessType && (
                    <Space>
                        <Typography.Text strong>{t('Access Type')}</Typography.Text>
                        <Typography.Text>{accessType}</Typography.Text>
                    </Space>
                )}
            </Flex>

            {tags.length > 0 && (
                <Space wrap>
                    {tags.map((tag) => (
                        <Tag color={tag.rolled_up ? 'red' : 'success'} key={tag.id}>
                            {tag.value}
                        </Tag>
                    ))}
                </Space>
            )}

            {description && <Typography.Text italic>{description}</Typography.Text>}
        </Flex>
    );
}
