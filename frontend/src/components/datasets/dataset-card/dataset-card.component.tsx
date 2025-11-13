import { Badge, Button, Card, Collapse, Flex, List, Popconfirm, Typography } from 'antd';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { useModal } from '@/hooks/use-modal';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useRemoveDatasetFromDataOutputMutation,
    useRequestDatasetAccessForDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useApproveDataOutputLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import { useGetDatasetByIdQuery, useRemoveDatasetMutation } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { createDatasetIdPath } from '@/types/navigation';
import { getBadgeStatus, getDecisionStatusBadgeStatus, getStatusLabel } from '@/utils/status.helper';
import { DataOutputLinkModal } from './data-output-link-modal.component';
import styles from './dataset-card.module.scss';

type Props = {
    datasetId: string;
    draggedDataOutputId?: string | null;
};

export function DatasetCard({ datasetId, draggedDataOutputId }: Props) {
    const { t } = useTranslation();
    const [dragOver, setDragOver] = useState(false);
    const [invalidDrop, setInvalidDrop] = useState(false);
    const { isVisible, handleOpen, handleClose } = useModal();

    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const { data: deleteAccess } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.DATASET__DELETE,
    });
    const { data: linkAccess } = useCheckAccessQuery({
        resource: dataset?.data_product_id,
        action: AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
    });

    const [removeDataset, { isLoading: isRemoving }] = useRemoveDatasetMutation();
    const [unlinkDataset] = useRemoveDatasetFromDataOutputMutation();
    const [linkDataset] = useRequestDatasetAccessForDataOutputMutation();
    const [approveLink] = useApproveDataOutputLinkMutation();

    const handleRemoveDataset = useCallback(async () => {
        if (!dataset) return;
        try {
            await removeDataset(dataset);
            dispatchMessage({
                content: t('Output port {{name}} has been successfully removed', { name: dataset.name }),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to remove output port'),
                type: 'error',
            });
        }
    }, [removeDataset, dataset, t]);

    const handleRemoveDataOutputLink = useCallback(
        async (dataOutputId: string) => {
            if (!dataset) return;
            try {
                await unlinkDataset({ dataOutputId, datasetId: dataset.id }).unwrap();
                dispatchMessage({
                    content: t('Technical asset unlinked successfully'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to unlink technical asset'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, dataset, t],
    );

    const handleDragOver = (event: React.DragEvent) => {
        event.preventDefault();
        // Check if the dragged technical asset is already linked to this dataset
        if (draggedDataOutputId && dataset) {
            const isAlreadyLinked = dataset.data_output_links?.some(
                (link) => link.data_output.id === draggedDataOutputId,
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
                const isAlreadyLinked = dataset.data_output_links?.some((link) => link.data_output.id === dragData.id);

                if (isAlreadyLinked) {
                    dispatchMessage({
                        content: t('Technical asset {{name}} is already linked to this output port', {
                            name: dragData.name,
                        }),
                        type: 'warning',
                    });
                    return;
                }

                const result = await linkDataset({ dataOutputId: dragData.id, datasetId: dataset.id }).unwrap();
                dispatchMessage({
                    content: t('Technical asset {{name}} linked to output port successfully', { name: dragData.name }),
                    type: 'success',
                });
                // TODO make this dependable on access rights
                await approveLink({
                    id: result.id,
                    data_output_id: dragData.id,
                    dataset_id: dataset.id,
                });
            }
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to link technical asset to output port'),
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
                                <Link to={createDatasetIdPath(dataset.id)}>
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
                                            'Are you sure you want to delete the output port? This can have impact on downstream dependencies',
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
                                ellipsis={{ expandable: 'collapsible' }}
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
                    {dataset.data_output_links && dataset.data_output_links.length > 0 && (
                        <Collapse
                            size={'small'}
                            items={[
                                {
                                    key: 0,
                                    label: t('{{count}} linked technical assets', {
                                        count: dataset.data_output_links.length,
                                    }),
                                    children: (
                                        <List
                                            size="small"
                                            dataSource={dataset.data_output_links}
                                            renderItem={(link) => (
                                                <List.Item>
                                                    <Flex justify="space-between" style={{ width: '100%' }}>
                                                        <Flex align="center" gap="small">
                                                            <Badge
                                                                status={getDecisionStatusBadgeStatus(link.status)}
                                                                size="small"
                                                            />
                                                            <Typography.Text>{link.data_output.name}</Typography.Text>
                                                        </Flex>
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            danger
                                                            onClick={() =>
                                                                handleRemoveDataOutputLink(link.data_output.id)
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
                    datasetName={dataset.name}
                    existingLinks={dataset.data_output_links || []}
                />
            )}
        </>
    );
}
