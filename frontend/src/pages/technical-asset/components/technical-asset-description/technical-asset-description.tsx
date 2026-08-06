import { Badge, Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { AccessModesField } from '@/components/access-modes/access-modes-field.component.tsx';
import type {
    AccessMode,
    TechnicalAssetStatus,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import type { TagModel } from '@/types/tag';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { getTechnicalAssetType } from '@/utils/technical-asset-type.helper.ts';

type Props = {
    status: TechnicalAssetStatus;
    type: string;
    description: string;
    tags: TagModel[];
    namespace: string;
    accessModes: AccessMode[];
};

export function TechnicalAssetDescription({ status, type, description, tags, namespace, accessModes }: Props) {
    const { t } = useTranslation();
    const { data: { plugins } = {} } = useGetPluginsQuery();

    return (
        <Flex vertical gap="medium">
            <Flex wrap gap="12px 36px">
                <Space>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Badge status={getBadgeStatus(status)} text={getStatusLabel(t, status)} />
                </Space>
                <Space>
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Space>
                <Space>
                    <Typography.Text strong>{t('Type')}</Typography.Text>
                    <Typography.Text>{getTechnicalAssetType(type, plugins, t)}</Typography.Text>
                </Space>
                <AccessModesField accessModes={accessModes} />
            </Flex>
            <Space size="small">
                {tags.map((tag) => (
                    <Tag color="success" key={tag.id}>
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
