import { QuestionCircleOutlined } from '@ant-design/icons';
import { Card, Descriptions, type DescriptionsProps, Flex, Tooltip, Typography, theme } from 'antd';
import type { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';
import AccessModeTag from '@/components/access-modes/access-mode.component.tsx';
import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import {
    AccessDurationSection,
    AccessTypeSection,
} from '@/components/output-ports/output-port-form/output-port-form.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    AbstractDataProductType,
    useGetAllAccessDurationsQuery,
} from '@/store/api/services/generated/configurationAccessDurationsApi.ts';
import {
    AccessDurationType,
    type DatasetUpdate,
    type OutputPortAccessDuration,
    useGetOutputPortAccessDurationsQuery,
    useGetOutputPortQuery,
    useUpdateOutputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    datasetId: string;
    dataProductId: string;
};

function formatAccessDuration(duration: OutputPortAccessDuration, t: TFunction): string {
    return duration.access_duration_type === AccessDurationType.Permanent
        ? t('Permanent')
        : t('{{count}} days', { count: duration.days });
}

export function SettingsTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const { data: outputPort, isLoading } = useGetOutputPortQuery(
        { id: datasetId, dataProductId },
        { skip: !datasetId || !dataProductId },
    );
    const { data: accessDurations } = useGetOutputPortAccessDurationsQuery(
        { dataProductId, id: datasetId },
        { skip: !datasetId || !dataProductId },
    );
    const { data: edit_access } = useCheckAccessQuery(
        { resource: datasetId, action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES },
        { skip: !datasetId },
    );
    const canEditAccess = edit_access?.allowed || false;
    const { data: allDurations = [] } = useGetAllAccessDurationsQuery();
    const [updateOutputPort] = useUpdateOutputPortMutation();

    if (isLoading) {
        return <LoadingSpinner />;
    }

    if (!outputPort) {
        return null;
    }

    async function saveAccessField(
        partial: Partial<
            Pick<
                DatasetUpdate,
                'access_type' | 'data_product_access_duration_type' | 'exploration_access_duration_type'
            >
        >,
    ) {
        if (!outputPort) return;
        try {
            await updateOutputPort({
                id: datasetId,
                dataProductId,
                datasetUpdate: {
                    name: outputPort.name,
                    namespace: outputPort.namespace,
                    description: outputPort.description,
                    tag_ids: outputPort.tags.map((tag) => tag.id),
                    lifecycle_id: outputPort.lifecycle?.id ?? null,
                    access_type: outputPort.access_type,
                    data_product_access_duration_type: outputPort.data_product_access_duration_type,
                    exploration_access_duration_type: outputPort.exploration_access_duration_type,
                    ...partial,
                },
            }).unwrap();
            dispatchMessage({ content: t('Output Port updated successfully'), type: 'success' });
        } catch {
            dispatchMessage({ content: t('Could not update Output Port'), type: 'error' });
        }
    }

    const durationsFor = (abstractDataProductType: AbstractDataProductType) =>
        allDurations.filter((d) => d.abstract_data_product_type === abstractDataProductType);

    const labelWithTooltip = (label: string, tooltip: string) => (
        <Flex align="center" gap="small">
            <span>{label}</span>
            <Tooltip title={tooltip}>
                <QuestionCircleOutlined style={{ color: token.colorTextTertiary }} />
            </Tooltip>
        </Flex>
    );

    const items: DescriptionsProps['items'] = [
        {
            key: 'access-settings',
            children: (
                <Flex vertical gap="middle">
                    <Flex vertical gap="small">
                        {labelWithTooltip(t('Access Type'), t('The access type of the Output Port'))}
                        {canEditAccess ? (
                            <AccessTypeSection
                                value={outputPort.access_type}
                                onChange={(value) => saveAccessField({ access_type: value })}
                            />
                        ) : (
                            getDatasetAccessTypeLabel(t, outputPort.access_type)
                        )}
                    </Flex>
                    {accessDurations && (
                        <Flex vertical gap="small">
                            {labelWithTooltip(
                                t('Access Duration'),
                                t(
                                    'Access duration policy configured by the administrator. This applies when someone requests access to this Output Port.',
                                ),
                            )}
                            <Flex vertical gap="small">
                                <Typography.Text type="secondary">{t('Data Products')}</Typography.Text>
                                {canEditAccess ? (
                                    <AccessDurationSection
                                        abstractDataProductType={AbstractDataProductType.DataProducts}
                                        accessDurations={durationsFor(AbstractDataProductType.DataProducts)}
                                        value={outputPort.data_product_access_duration_type}
                                        onChange={(value) =>
                                            saveAccessField({ data_product_access_duration_type: value })
                                        }
                                    />
                                ) : (
                                    <Typography.Text>
                                        {formatAccessDuration(accessDurations.data_product_access_duration, t)}
                                    </Typography.Text>
                                )}
                            </Flex>
                            <Flex vertical gap="small">
                                <Typography.Text type="secondary">{t('Explorations')}</Typography.Text>
                                {canEditAccess ? (
                                    <AccessDurationSection
                                        abstractDataProductType={AbstractDataProductType.Explorations}
                                        accessDurations={durationsFor(AbstractDataProductType.Explorations)}
                                        value={outputPort.exploration_access_duration_type}
                                        onChange={(value) =>
                                            saveAccessField({ exploration_access_duration_type: value })
                                        }
                                    />
                                ) : (
                                    <Typography.Text>
                                        {formatAccessDuration(accessDurations.exploration_access_duration, t)}
                                    </Typography.Text>
                                )}
                            </Flex>
                        </Flex>
                    )}
                </Flex>
            ),
        },
        {
            key: 'access-modes',
            label: t('Access modes'),
            children:
                outputPort.access_modes.length === 0 ? (
                    t('None')
                ) : (
                    <Flex gap="small" wrap>
                        {outputPort.access_modes.map((accessMode) => (
                            <AccessModeTag key={accessMode.id} accessMode={accessMode} />
                        ))}
                    </Flex>
                ),
        },
    ];

    return (
        <Flex vertical gap="middle">
            <Card title={t('Access Settings')} size="small">
                <Descriptions
                    column={1}
                    layout="vertical"
                    size="small"
                    items={items}
                    styles={{ label: { color: token.colorTextSecondary } }}
                />
            </Card>
            <Card title={t('Custom Settings')} size="small">
                <DataProductSettings id={datasetId} scope="dataset" dataProductId={dataProductId} />
            </Card>
        </Flex>
    );
}
