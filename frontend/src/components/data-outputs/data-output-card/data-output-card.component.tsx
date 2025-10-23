import { DownOutlined, HolderOutlined, RightOutlined } from '@ant-design/icons';
import { Badge, Button, Card, Flex, List, Popconfirm, Tooltip, Typography } from 'antd';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useRemoveDataOutputDatasetLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputsGetContract } from '@/types/data-output';
import { createDataOutputIdPath } from '@/types/navigation';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { getDecisionStatusBadgeStatus } from '@/utils/status.helper';

import styles from './data-output-card.module.scss';

type Props = {
    dataOutput: DataOutputsGetContract[0];
    dataProductId: string;
    onDragStart?: () => void;
    onDragEnd?: () => void;
};

export function DataOutputCard({ dataOutput, dataProductId, onDragStart, onDragEnd }: Props) {
    const { t } = useTranslation();
    const [expanded, setExpanded] = useState(false);

    const { data: deleteAccess } = useCheckAccessQuery({
        resource: dataProductId,
        action: AuthorizationAction.DATA_PRODUCT__DELETE_DATA_OUTPUT,
    });

    const [removeDataOutput, { isLoading: isRemoving }] = useRemoveDataOutputMutation();
    const [unlinkDataset] = useRemoveDataOutputDatasetLinkMutation();

    const handleRemoveDataOutput = useCallback(async () => {
        try {
            await removeDataOutput(dataOutput.id).unwrap();
            dispatchMessage({
                content: t('Data Output {{name}} has been successfully removed', { name: dataOutput.name }),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to remove data output'),
                type: 'error',
            });
        }
    }, [removeDataOutput, dataOutput.id, dataOutput.name, t]);

    const handleRemoveDatasetLink = useCallback(
        async (datasetId: string, datasetLinkId: string) => {
            try {
                await unlinkDataset({ dataOutputId: dataOutput.id, datasetId, datasetLinkId }).unwrap();
                dispatchMessage({
                    content: t('Dataset unlinked successfully'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to unlink dataset'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, dataOutput.id, t],
    );

    const handleDragStart = (event: React.DragEvent) => {
        event.dataTransfer.setData(
            'text/plain',
            JSON.stringify({
                type: 'data-output',
                id: dataOutput.id,
                name: dataOutput.name,
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

    const getDeleteDescription = () => {
        if (dataOutput.dataset_links && dataOutput.dataset_links.length > 0) {
            return (
                <Flex vertical>
                    {t(
                        'Are you sure you want to delete this technical asset? This asset is still used in the following output ports:',
                    )}
                    <List
                        size="small"
                        dataSource={dataOutput.dataset_links}
                        renderItem={(link) => (
                            <List.Item style={{ padding: '0 0', border: 'none' }}>• {link.dataset.name}</List.Item>
                        )}
                    />
                </Flex>
            );
        }
        return t(
            'Are you sure you want to delete this technical asset? This can have impact on downstream dependencies',
        );
    };

    return (
        <Card className={styles.card} draggable onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <Flex className={styles.cardContent}>
                <Flex className={styles.dragHandle}>
                    <HolderOutlined />
                </Flex>
                <Flex vertical className={styles.mainContent}>
                    <Flex justify="space-between" align="flex-start">
                        <Flex gap={12} align="center">
                            <CustomSvgIconLoader
                                iconComponent={getDataOutputIcon(dataOutput.configuration.configuration_type)}
                            />
                            <Flex>
                                <Link to={createDataOutputIdPath(dataOutput.id, dataOutput.owner_id)}>
                                    <Typography.Title
                                        level={5}
                                        ellipsis={{ tooltip: true, rows: 2 }}
                                        style={{ margin: 0 }}
                                    >
                                        {dataOutput.result_string || ''}
                                    </Typography.Title>
                                    <Typography.Text ellipsis={{ tooltip: true }} type="secondary">
                                        {dataOutput.name}
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

                    {dataOutput.dataset_links && dataOutput.dataset_links.length > 0 && (
                        <Flex vertical align="flex-start">
                            <Button
                                type="text"
                                size="small"
                                onClick={() => setExpanded(!expanded)}
                                className={styles.expandButton}
                                icon={expanded ? <DownOutlined /> : <RightOutlined />}
                            >
                                {t('{{count}} linked output ports', { count: dataOutput.dataset_links.length })}
                            </Button>

                            {expanded && (
                                <Flex align="flex-end" justify="space-between" className={styles.linkedDatasetsList}>
                                    <List
                                        style={{ width: '100%' }}
                                        size="small"
                                        dataSource={dataOutput.dataset_links}
                                        renderItem={(link) => (
                                            <List.Item className={styles.linkedDatasetItem}>
                                                <Flex justify="space-between" align="center" style={{ width: '100%' }}>
                                                    <Flex align="center" gap={8}>
                                                        <Badge
                                                            status={getDecisionStatusBadgeStatus(link.status)}
                                                            size="small"
                                                        />
                                                        <Typography.Text className={styles.datasetName}>
                                                            {link.dataset.name}
                                                        </Typography.Text>
                                                    </Flex>
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        danger
                                                        onClick={() =>
                                                            handleRemoveDatasetLink(link.dataset.id, link.id)
                                                        }
                                                    >
                                                        {t('Remove')}
                                                    </Button>
                                                </Flex>
                                            </List.Item>
                                        )}
                                    />
                                </Flex>
                            )}
                        </Flex>
                    )}
                </Flex>
            </Flex>
        </Card>
    );
}
