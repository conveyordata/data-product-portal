import { Badge, Button, Card, Collapse, Flex, List, Popconfirm, Typography } from 'antd';
import { type DragEvent, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { useModal } from '@/hooks/use-modal';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetOutputPortQuery,
    useRemoveOutputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    useApproveOutputPortTechnicalAssetLinkMutation,
    useLinkOutputPortToTechnicalAssetMutation,
    useUnlinkOutputPortFromTechnicalAssetMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation';
import { getBadgeStatus, getDecisionStatusBadgeStatus, getStatusLabel } from '@/utils/status.helper';
import { DataOutputLinkModal } from './data-output-link-modal.component';
import styles from './dataset-card.module.scss';

type Props = {
    datasetId: string;
    dataProductId: string;
    draggedDataOutputId?: string | null;
};

export function DatasetCard({ datasetId, dataProductId, draggedDataOutputId }: Props) {
    const { t } = useTranslation();
    const [dragOver, setDragOver] = useState(false);
    const [invalidDrop, setInvalidDrop] = useState(false);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [isRemoved, setIsRemoved] = useState(false);

    const { data: dataset, isLoading } = useGetOutputPortQuery({ id: datasetId, dataProductId }, { skip: isRemoved });
    const { data: deleteAccess } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.OUTPUT_PORT__DELETE,
    });
    const { data: linkAccess } = useCheckAccessQuery({
        resource: dataset?.data_product_id,
        action: AuthorizationAction.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
    });

    const [removeDataset, { isLoading: isRemoving }] = useRemoveOutputPortMutation();
    const [unlinkDataset] = useUnlinkOutputPortFromTechnicalAssetMutation();
    const [linkDataset] = useLinkOutputPortToTechnicalAssetMutation();
    const [approveLink] = useApproveOutputPortTechnicalAssetLinkMutation();

    const handleRemoveDataset = useCallback(async () => {
        setIsRemoved(true);
        if (!dataset) return;
        try {
            await removeDataset({ id: datasetId, dataProductId }).unwrap();
            dispatchMessage({
                content: t('Output Port {{name}} has been successfully removed', { name: dataset.name }),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to remove Output Port'),
                type: 'error',
            });
        }
    }, [removeDataset, dataset, t, dataProductId, datasetId]);

    const handleRemoveDataOutputLink = useCallback(
        async (dataOutputId: string) => {
            if (!dataset) return;
            try {
                await unlinkDataset({
                    outputPortId: datasetId,
                    dataProductId,
                    unLinkTechnicalAssetToOutputPortRequest: { technical_asset_id: dataOutputId },
                }).unwrap();
                dispatchMessage({
                    content: t('Technical Asset unlinked successfully'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to unlink Technical Asset'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, dataset, t, dataProductId, datasetId],
    );

    const handleDragOver = (event: DragEvent) => {
        event.preventDefault();
        // Check if the dragged Technical Asset is already linked to this dataset
        if (draggedDataOutputId && dataset) {
            const isAlreadyLinked = dataset.technical_asset_links?.some(
                (link) => link.technical_asset_id === draggedDataOutputId,
            );

            if (isAlreadyLinked) {
                event.dataTransfer.dropEffect = 'none';
                setInvalidDrop(true);
                setDragOver(false);
                return;
            }
        }

        event.dataTransfer.dropEffect = 'copy';
        setInvalidDrop(false);
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
        setInvalidDrop(false);
    };

    const handleDrop = async (event: React.DragEvent) => {
        event.preventDefault();
        setDragOver(false);

        try {
            const dragData = JSON.parse(event.dataTransfer.getData('text/plain'));
            if (dragData.type === 'data-output' && dataset) {
                // Check if already linked
                const isAlreadyLinked = dataset.technical_asset_links?.some(
                    (link) => link.technical_asset_id === dragData.id,
                );

                if (isAlreadyLinked) {
                    dispatchMessage({
                        content: t('Technical Asset {{name}} is already linked to this Output Port', {
                            name: dragData.name,
                        }),
                        type: 'warning',
                    });
                    return;
                }

                await linkDataset({
                    outputPortId: dataset.id,
                    dataProductId,
                    linkTechnicalAssetToOutputPortRequest: {
                        technical_asset_id: dragData.id,
                    },
                }).unwrap();
                dispatchMessage({
                    content: t('Technical Asset {{name}} linked to Output Port successfully', { name: dragData.name }),
                    type: 'success',
                });
                // TODO make this dependable on access rights
                await approveLink({
                    dataProductId,
                    outputPortId: datasetId,
                    approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                        technical_asset_id: dragData.id,
                    },
                }).unwrap();
            }
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to link Technical Asset to Output Port'),
                type: 'error',
            });
        }
    };

    const handleMouseDown = (event: React.MouseEvent) => {
        // Prevent drag start on interactive elements
        const target = event.target as HTMLElement;
        if (target.closest('button, a, .ant-btn, [role="button"]')) {
            event.preventDefault();
            event.stopPropagation();
        }
    };

    if (isLoading || !dataset) {
        return <Card loading={true} className={styles.card} />;
    }

    const canLink = linkAccess?.allowed ?? false;
    const canRemove = deleteAccess?.allowed ?? false;

    return (
        <>
            <Card
                className={`${styles.card}  ${dragOver ? styles.dragOver : ''} ${invalidDrop ? styles.invalidDrop : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onMouseDown={handleMouseDown}
            >
                <Flex vertical gap="small">
                    <Flex gap="small" align="center">
                        <CustomSvgIconLoader iconComponent={datasetBorderIcon} />
                        <Flex vertical flex={1} style={{ minWidth: 0 }}>
                            {' '}
                            {/*Min width is needed to ensure the elipsis of description*/}
                            <Flex justify="space-between" align="flex-start">
                                <Link to={createMarketplaceOutputPortPath(dataset.id, dataset.data_product_id)}>
                                    <Typography.Title level={5}>{dataset.name}</Typography.Title>
                                </Link>
                                <Flex gap="small">
                                    <Button
                                        onClick={handleOpen}
                                        loading={isRemoving}
                                        disabled={!canLink}
                                        type="link"
                                        size="small"
                                    >
                                        {t('Link Technical Assets')}
                                    </Button>
                                    <Popconfirm
                                        title={t('Remove')}
                                        description={t(
                                            'Are you sure you want to delete the Output Port? This can have impact on downstream dependencies',
                                        )}
                                        onConfirm={handleRemoveDataset}
                                        placement="topRight"
                                        okText={t('Confirm')}
                                        cancelText={t('Cancel')}
                                        okButtonProps={{ loading: isRemoving }}
                                    >
                                        <Button
                                            loading={isRemoving}
                                            disabled={!canRemove}
                                            type="text"
                                            size="small"
                                            danger
                                        >
                                            {t('Remove')}
                                        </Button>
                                    </Popconfirm>
                                </Flex>
                            </Flex>
                            <Typography.Paragraph
                                style={{ marginBottom: 0 }}
                                type="secondary"
                                ellipsis={{
                                    expandable: 'collapsible',
                                    symbol: (expanded: boolean) => (expanded ? t('less') : t('more')),
                                }}
                            >
                                {dataset.description}
                            </Typography.Paragraph>
                        </Flex>
                    </Flex>

                    <Badge
                        className={styles.badge}
                        status={getBadgeStatus(dataset.status)}
                        text={getStatusLabel(t, dataset.status)}
                    />
                    {dataset.technical_asset_links && dataset.technical_asset_links.length > 0 && (
                        <Collapse
                            size={'small'}
                            items={[
                                {
                                    key: 0,
                                    label: t('{{count}} linked Technical Assets', {
                                        count: dataset.technical_asset_links.length,
                                    }),
                                    children: (
                                        <List
                                            size="small"
                                            dataSource={dataset.technical_asset_links}
                                            renderItem={(link) => (
                                                <List.Item>
                                                    <Flex justify="space-between" style={{ width: '100%' }}>
                                                        <Flex align="center" gap="small">
                                                            <Badge
                                                                status={getDecisionStatusBadgeStatus(link.status)}
                                                                size="small"
                                                            />
                                                            <Typography.Text>
                                                                {link.technical_asset.name}
                                                            </Typography.Text>
                                                        </Flex>
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            danger
                                                            onClick={() =>
                                                                handleRemoveDataOutputLink(link.technical_asset_id)
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
            </Card>

            {isVisible && (
                <DataOutputLinkModal
                    onClose={handleClose}
                    datasetId={datasetId}
                    dataProductId={dataProductId}
                    datasetName={dataset.name}
                    existingLinks={dataset.technical_asset_links || []}
                />
            )}
        </>
    );
}
