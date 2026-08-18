import { Card, Descriptions, type DescriptionsProps, Flex, Typography, theme } from 'antd';
import type { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';
import AccessModeTag from '@/components/access-modes/access-mode.component.tsx';
import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import {
    AccessDurationType,
    type OutputPortAccessDuration,
    useGetOutputPortAccessDurationsQuery,
    useGetOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';

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
    const { data: outputPort, isFetching } = useGetOutputPortQuery(
        { id: datasetId, dataProductId },
        { skip: !datasetId || !dataProductId },
    );
    const { data: accessDurations } = useGetOutputPortAccessDurationsQuery(
        { dataProductId, id: datasetId },
        { skip: !datasetId || !dataProductId },
    );

    if (isFetching) {
        return <LoadingSpinner />;
    }

    if (!outputPort) {
        return null;
    }

    const items: DescriptionsProps['items'] = [
        {
            key: 'access-type',
            label: t('Access Type'),
            children: getDatasetAccessTypeLabel(t, outputPort.access_type),
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
        ...(accessDurations
            ? [
                  {
                      key: 'timebound-access',
                      label: t('Access Duration'),
                      children: (
                          <Flex vertical gap="small">
                              <Typography.Text>
                                  {t('Data Products')}:{' '}
                                  {formatAccessDuration(accessDurations.data_product_access_duration, t)}
                              </Typography.Text>
                              <Typography.Text>
                                  {t('Explorations')}:{' '}
                                  {formatAccessDuration(accessDurations.exploration_access_duration, t)}
                              </Typography.Text>
                          </Flex>
                      ),
                  },
              ]
            : []),
    ];

    return (
        <Flex gap="medium" align="stretch">
            <Card title={t('Access')} size="small" style={{ flex: 1 }}>
                <Descriptions
                    column={1}
                    layout="vertical"
                    size="small"
                    items={items}
                    styles={{ label: { color: token.colorTextSecondary } }}
                />
            </Card>
            <Card title={t('Custom Settings')} size="small" style={{ flex: 2 }}>
                <DataProductSettings id={datasetId} scope="dataset" dataProductId={dataProductId} />
            </Card>
        </Flex>
    );
}
