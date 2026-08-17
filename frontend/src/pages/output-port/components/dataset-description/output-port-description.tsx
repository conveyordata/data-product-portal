import { Flex, Space, Tag, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { AccessModesField } from '@/components/access-modes/access-modes-field.component.tsx';
import type { GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    AccessDurationType,
    type AccessMode,
    type DataProductLifeCycle,
    type GetOutputPortAccessDurationsResponse,
    type OutputPortAccessDuration,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
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
    accessModes: AccessMode[];
    accessDurations?: GetOutputPortAccessDurationsResponse;
};

function formatAccessDuration(duration: OutputPortAccessDuration, t: TFunction): string {
    return duration.access_duration_type === AccessDurationType.Permanent
        ? t('Permanent')
        : t('{{count}} days', { count: duration.days });
}

export function OutputPortDescription({
    lifecycle,
    accessType,
    description,
    data_product,
    domain,
    tags,
    namespace,
    accessModes,
    accessDurations,
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
                <AccessModesField accessModes={accessModes} />

                {accessDurations && (
                    <>
                        <Space>
                            <Typography.Text strong>{t('Data Product Access')}</Typography.Text>
                            <Typography.Text>
                                {formatAccessDuration(accessDurations.data_product_access_duration, t)}
                            </Typography.Text>
                        </Space>
                        <Space>
                            <Typography.Text strong>{t('Exploration Access')}</Typography.Text>
                            <Typography.Text>
                                {formatAccessDuration(accessDurations.exploration_access_duration, t)}
                            </Typography.Text>
                        </Space>
                    </>
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
