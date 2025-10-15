import Icon, { DeleteOutlined } from '@ant-design/icons';
import { Badge, Button, Card, Flex, Popconfirm, Tag, Typography } from 'antd';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
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
import styles from './dataset-card.module.scss';

type Props = {
    datasetId: string;
    isDragActive?: boolean;
    draggedDataOutputId?: string | null;
};

export function DatasetCard({ datasetId, isDragActive, draggedDataOutputId }: Props) {
    const { t } = useTranslation();
    const [dragOver, setDragOver] = useState(false);
    const [invalidDrop, setInvalidDrop] = useState(false);

    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const { data: deleteAccess } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.DATASET__DELETE,
    });

    const [removeDataset, { isLoading: isRemoving }] = useRemoveDatasetMutation();
    const [unlinkDataset] = useRemoveDatasetFromDataOutputMutation();
    const [linkDataset] = useRequestDatasetAccessForDataOutputMutation();
    const [approveLink] = useApproveDataOutputLinkMutation();

    const handleRemoveDataset = useCallback(async () => {
        if (!dataset) return;
        try {
            await removeDataset(dataset.id).unwrap();
            dispatchMessage({
                content: t('Dataset {{name}} has been successfully removed', { name: dataset.name }),
                type: 'success',
            });
        } catch (error) {
            console.error('Failed to remove dataset', error);
        }
    }, [removeDataset, dataset, t]);

    const handleRemoveDataOutputLink = useCallback(
        async (dataOutputId: string) => {
            if (!dataset) return;
            try {
                await unlinkDataset({ dataOutputId, datasetId: dataset.id }).unwrap();
                dispatchMessage({
                    content: t('Data output unlinked successfully'),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to unlink data output', error);
                dispatchMessage({
                    content: t('Failed to unlink data output'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, dataset, t],
    );

    const handleDragOver = (event: React.DragEvent) => {
        event.preventDefault();
        // Check if the dragged data output is already linked to this dataset
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
                        content: t('Data output {{name}} is already linked to this dataset', { name: dragData.name }),
                        type: 'warning',
                    });
                    return;
                }

                const result = await linkDataset({ dataOutputId: dragData.id, datasetId: dataset.id }).unwrap();
                dispatchMessage({
                    content: t('Data output {{name}} linked to dataset successfully', { name: dragData.name }),
                    type: 'success',
                });
                // TODO make this dependable on access rights
                await approveLink({ id: result.id, data_output_id: dragData.id, dataset_id: dataset.id }).unwrap();
            }
        } catch (error) {
            console.error('Failed to link data output to dataset:', error);
            dispatchMessage({
                content: t('Failed to link data output to dataset'),
                type: 'error',
            });
        }
    };

    if (isLoading || !dataset) {
        return <Card loading={true} className={styles.card} />;
    }

    const canRemove = deleteAccess?.allowed ?? false;

    return (
        <Card
            className={`${styles.card} ${isDragActive ? styles.dropZone : ''} ${dragOver ? styles.dragOver : ''} ${invalidDrop ? styles.invalidDrop : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <Flex vertical gap={12}>
                <Flex justify="space-between" align="flex-start">
                    <div>
                        <Link to={createDatasetIdPath(dataset.id)}>
                            <Typography.Title level={5} className={styles.title}>
                                {dataset.name}
                            </Typography.Title>
                            <Typography.Text type="secondary" className={styles.description}>
                                {dataset.description}
                            </Typography.Text>
                        </Link>
                    </div>
                    <Popconfirm
                        title={t('Remove')}
                        description={t(
                            'Are you sure you want to delete the dataset? This can have impact on downstream dependencies',
                        )}
                        onConfirm={handleRemoveDataset}
                        placement="topRight"
                        okText={t('Confirm')}
                        cancelText={t('Cancel')}
                        okButtonProps={{ loading: isRemoving }}
                    >
                        <Button loading={isRemoving} disabled={!canRemove} type="text" size="small" danger>
                            {t('Delete')}
                        </Button>
                    </Popconfirm>
                </Flex>

                <Flex vertical gap={8}>
                    <Badge status={getBadgeStatus(dataset.status)} text={getStatusLabel(t, dataset.status)} />

                    {dataset.data_output_links && dataset.data_output_links.length > 0 && (
                        <Flex wrap gap={4}>
                            {dataset.data_output_links.map((link) => (
                                <Tag
                                    key={link.data_output.id}
                                    color="blue"
                                    closeIcon={<Icon component={DeleteOutlined} />}
                                    closable
                                    onClose={(e) => {
                                        e.preventDefault();
                                        handleRemoveDataOutputLink(link.data_output.id);
                                    }}
                                >
                                    <Badge
                                        className={styles.badge}
                                        status={getDecisionStatusBadgeStatus(link.status)}
                                    />
                                    {link.data_output.name}
                                </Tag>
                            ))}
                        </Flex>
                    )}
                </Flex>
            </Flex>
        </Card>
    );
}
