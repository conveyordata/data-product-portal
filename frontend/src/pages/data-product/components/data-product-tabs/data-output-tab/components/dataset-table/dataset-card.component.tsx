import { Badge, Button, Card, Flex, Popconfirm, Tag, Typography } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDatasetFromDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDatasetByIdQuery, useRemoveDatasetMutation } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper';

import styles from './dataset-card.module.scss';

type Props = {
    datasetId: string;
};

export function DatasetCard({ datasetId }: Props) {
    const { t } = useTranslation();

    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const { data: deleteAccess } = useCheckAccessQuery({
        resource: datasetId,
        action: AuthorizationAction.DATASET__DELETE,
    });

    const [removeDataset, { isLoading: isRemoving }] = useRemoveDatasetMutation();
    const [unlinkDataset] = useRemoveDatasetFromDataOutputMutation();

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

    if (isLoading || !dataset) {
        return <Card loading={true} className={styles.card} />;
    }

    const canRemove = deleteAccess?.allowed ?? false;

    return (
        <Card className={styles.card}>
            <Flex vertical gap={12}>
                <Flex justify="space-between" align="flex-start">
                    <div>
                        <Typography.Title level={5} className={styles.title}>
                            {dataset.name}
                        </Typography.Title>
                        <Typography.Text type="secondary" className={styles.description}>
                            {dataset.description}
                        </Typography.Text>
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
                            {t('Remove')}
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
                                    closable
                                    onClose={(e) => {
                                        e.preventDefault();
                                        handleRemoveDataOutputLink(link.data_output.id);
                                    }}
                                >
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
