import { Badge, Button, Card, Flex, Popconfirm, Tag, Typography } from 'antd';
import { useCallback } from 'react';
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
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper';

import styles from './data-output-card.module.scss';

type Props = {
    dataOutput: DataOutputsGetContract[0];
    dataProductId: string;
};

export function DataOutputCard({ dataOutput, dataProductId }: Props) {
    const { t } = useTranslation();

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
        } catch (error) {
            console.error('Failed to remove data output', error);
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
            } catch (error) {
                console.error('Failed to unlink dataset', error);
                dispatchMessage({
                    content: t('Failed to unlink dataset'),
                    type: 'error',
                });
            }
        },
        [unlinkDataset, dataOutput.id, t],
    );

    const canRemove = deleteAccess?.allowed ?? false;

    return (
        <Card className={styles.card}>
            <Flex vertical gap={12}>
                <Flex justify="space-between" align="flex-start">
                    <Flex gap={12} align="flex-start">
                        <CustomSvgIconLoader
                            iconComponent={getDataOutputIcon(dataOutput.configuration.configuration_type)}
                        />
                        <div className={styles.content}>
                            <Link to={createDataOutputIdPath(dataOutput.id, dataOutput.owner_id)}>
                                <Typography.Title level={5} className={styles.title}>
                                    {dataOutput.name}
                                </Typography.Title>
                            </Link>
                            <Typography.Text type="secondary" className={styles.description}>
                                {dataOutput.description}
                            </Typography.Text>
                        </div>
                    </Flex>
                    <Popconfirm
                        title={t('Remove')}
                        description={t(
                            'Are you sure you want to delete the data output? This can have impact on downstream dependencies',
                        )}
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

                <Flex vertical gap={8}>
                    <Badge status={getBadgeStatus(dataOutput.status)} text={getStatusLabel(t, dataOutput.status)} />

                    {dataOutput.dataset_links && dataOutput.dataset_links.length > 0 && (
                        <Flex wrap gap={4}>
                            {dataOutput.dataset_links.map((link) => (
                                <Tag
                                    key={link.dataset.id}
                                    color="green"
                                    closable
                                    onClose={(e) => {
                                        e.preventDefault();
                                        handleRemoveDatasetLink(link.dataset.id, link.id);
                                    }}
                                >
                                    {link.dataset.name}
                                </Tag>
                            ))}
                        </Flex>
                    )}
                </Flex>
            </Flex>
        </Card>
    );
}
