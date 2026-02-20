import { HolderOutlined } from '@ant-design/icons';
import { Badge, Button, Card, Collapse, Flex, List, Popconfirm, Tooltip, Typography } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type GetTechnicalAssetsResponseItemRead,
    TechnicalAssetStatus,
    useRemoveTechnicalAssetMutation,
    useUnlinkOutputPortFromTechnicalAssetMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { createDataOutputIdPath } from '@/types/navigation';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { getDecisionStatusBadgeStatus } from '@/utils/status.helper';
import styles from './data-output-card.module.scss';

type Props = {
    technicalAsset: GetTechnicalAssetsResponseItemRead;
    dataProductId: string;
    onDragStart?: () => void;
    onDragEnd?: () => void;
};

export function TechnicalAssetCard({ technicalAsset, dataProductId, onDragStart, onDragEnd }: Props) {
    const { t } = useTranslation();
    const { data: { plugins } = {} } = useGetPluginsQuery();
    const { data: deleteAccess } = useCheckAccessQuery({
        resource: dataProductId,
        action: AuthorizationAction.DATA_PRODUCT__DELETE_TECHNICAL_ASSET,
    });

    const [removeDataOutput, { isLoading: isRemoving }] = useRemoveTechnicalAssetMutation();
    const [unlinkDataset] = useUnlinkOutputPortFromTechnicalAssetMutation();

    const handleRemoveDataOutput = useCallback(async () => {
        try {
            await removeDataOutput({ id: technicalAsset.id, dataProductId }).unwrap();
            dispatchMessage({
                content: t('Technical Asset {{name}} has been successfully removed', { name: technicalAsset.name }),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to remove Technical Asset'),
                type: 'error',
            });
        }
    }, [removeDataOutput, technicalAsset.id, technicalAsset.name, t, dataProductId]);

    const handleRemoveDatasetLink = useCallback(
        async (datasetId: string, technical_asset_id: string) => {
            try {
                await unlinkDataset({
                    outputPortId: datasetId,
                    dataProductId,
                    unLinkTechnicalAssetToOutputPortRequest: { technical_asset_id },
                }).unwrap();
                dispatchMessage({
                    content: t('Output Port unlinked successfully'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to unlink Output Port'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, dataProductId, t],
    );

    const handleDragStart = (event: React.DragEvent) => {
        event.dataTransfer.setData(
            'text/plain',
            JSON.stringify({
                type: 'data-output',
                id: technicalAsset.id,
                name: technicalAsset.name,
            }),
        );

        event.dataTransfer.effectAllowed = 'copyMove';

        // Add dragging class to the card
        const cardElement = event.currentTarget as HTMLElement;
        cardElement.classList.add(styles.dragging);

        onDragStart?.();
    };

    const handleDragEnd = (event: React.DragEvent) => {
        const cardElement = event.currentTarget as HTMLElement;
        cardElement.classList.remove(styles.dragging);
        onDragEnd?.();
    };

    const canRemove = deleteAccess?.allowed ?? false;
    const isActive = technicalAsset.status === TechnicalAssetStatus.Active;

    const getDeleteDescription = () => {
        if (technicalAsset.output_port_links && technicalAsset.output_port_links.length > 0) {
            return (
                <Flex vertical>
                    {t(
                        'Are you sure you want to delete this Technical Asset? This asset is still used in the following Output Ports:',
                    )}
                    <List
                        size="small"
                        dataSource={technicalAsset.output_port_links}
                        renderItem={(link) => (
                            <List.Item style={{ padding: '0 0', border: 'none' }}>• {link.output.name}</List.Item>
                        )}
                    />
                </Flex>
            );
        }
        return t(
            'Are you sure you want to delete this Technical Asset? This can have impact on downstream dependencies',
        );
    };

    return (
        <Card
            className={styles.card}
            draggable={isActive}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            size="small"
        >
            <Flex gap={'middle'}>
                {isActive ? (
                    <HolderOutlined />
                ) : (
                    <Tooltip
                        title={t(
                            'This technical asset is in pending state, please consult your platform administrator to activate it',
                        )}
                    >
                        <HolderOutlined style={{ cursor: 'not-allowed', opacity: 0.5 }} />
                    </Tooltip>
                )}
                <Flex vertical flex={1} gap={'middle'}>
                    <Flex justify="space-between" align="flex-start">
                        <Flex gap={'middle'} align="center">
                            <CustomSvgIconLoader
                                iconComponent={getDataOutputIcon(
                                    technicalAsset.configuration.configuration_type,
                                    plugins,
                                )}
                            />
                            <Flex>
                                <Link to={createDataOutputIdPath(technicalAsset.id, technicalAsset.owner_id)}>
                                    <Typography.Title
                                        level={5}
                                        ellipsis={{ tooltip: true, rows: 2 }}
                                        style={{ margin: 0 }}
                                    >
                                        {technicalAsset.result_string || ''}
                                    </Typography.Title>
                                    <Typography.Text ellipsis={{ tooltip: true }} type="secondary">
                                        {technicalAsset.name}
                                    </Typography.Text>
                                </Link>
                            </Flex>
                        </Flex>
                        <Popconfirm
                            title={t('Remove Technical Asset')}
                            description={getDeleteDescription()}
                            onConfirm={handleRemoveDataOutput}
                            placement="topRight"
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isRemoving }}
                        >
                            <Button loading={isRemoving} disabled={!canRemove} type="text" size="small" danger>
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    </Flex>

                    {technicalAsset.output_port_links && technicalAsset.output_port_links.length > 0 && (
                        <Collapse
                            size={'small'}
                            items={[
                                {
                                    key: '1',
                                    label: t('{{count}} linked Output Ports', {
                                        count: technicalAsset.output_port_links.length,
                                    }),
                                    /*    style: {
                                    paddingRight: 0,
                                    // marginBottom: 24,
                                    // background: 'red',
                                    // borderRadius: token.borderRadiusLG,
                                    border: 'none',
                                },*/

                                    children: (
                                        <List
                                            size="small"
                                            dataSource={technicalAsset.output_port_links}
                                            renderItem={(link) => (
                                                <List.Item>
                                                    <Flex
                                                        justify="space-between"
                                                        align="center"
                                                        style={{ width: '100%' }}
                                                    >
                                                        <Flex align="center" gap={8}>
                                                            <Badge
                                                                status={getDecisionStatusBadgeStatus(link.status)}
                                                                size="small"
                                                            />
                                                            <Typography.Text>{link.output.name}</Typography.Text>
                                                        </Flex>
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            danger
                                                            onClick={() =>
                                                                handleRemoveDatasetLink(
                                                                    link.output.id,
                                                                    link.technical_asset_id,
                                                                )
                                                            }
                                                        >
                                                            {t('Remove')}
                                                        </Button>
                                                    </Flex>
                                                </List.Item>
                                            )}
                                        />
                                    ),
                                },
                            ]}
                        />
                    )}
                </Flex>
            </Flex>
        </Card>
    );
}
