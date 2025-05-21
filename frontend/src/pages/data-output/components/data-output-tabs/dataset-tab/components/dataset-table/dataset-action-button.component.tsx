import { Button, Popconfirm } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useRemoveDatasetFromDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DatasetContract } from '@/types/dataset';
import { DecisionStatus } from '@/types/roles';

type Props = {
    dataset: DatasetContract;
    dataOutputId: string;
    dataProductId: string | undefined;
    status: DecisionStatus;
};
export function DatasetActionButton({ dataset, dataOutputId, dataProductId, status }: Props) {
    const { t } = useTranslation();

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
        },
        { skip: !dataProductId },
    );
    const canRevoke = access?.allowed ?? false;

    const [removeDatasetFromDataOutput, { isLoading }] = useRemoveDatasetFromDataOutputMutation();

    const handleRemoveDatasetFromDataOutput = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataOutput({ datasetId, dataOutputId: dataOutputId }).unwrap();
                dispatchMessage({
                    content: t('Dataset {{name}} has been removed from data output', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove dataset from data output', error);
            }
        },
        [dataOutputId, removeDatasetFromDataOutput, t],
    );

    const handleCancelDatasetLinkRequest = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataOutput({ datasetId, dataOutputId }).unwrap();
                dispatchMessage({
                    content: t('Request to link dataset {{name}} has been cancelled', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to cancel dataset link request', error);
            }
        },
        [dataOutputId, removeDatasetFromDataOutput, t],
    );

    const buttonText = status === DecisionStatus.Pending ? t('Cancel') : t('Remove');
    const popupTitle = status === DecisionStatus.Pending ? t('Cancel Request') : t('Unlink Dataset');
    const popupDescription =
        status === DecisionStatus.Pending
            ? t('Are you sure you want to cancel the request to link {{name}} to the data output?', {
                  name: dataset.name,
              })
            : t('Are you sure you want to remove {{name}} from the data output?', {
                  name: dataset.name,
              });
    const onConfirm =
        status === DecisionStatus.Pending ? handleCancelDatasetLinkRequest : handleRemoveDatasetFromDataOutput;

    return (
        <Popconfirm
            title={popupTitle}
            description={popupDescription}
            onConfirm={() => onConfirm(dataset.id, dataset.name)}
            placement={'leftTop'}
            okText={t('Confirm')}
            cancelText={t('Cancel')}
            okButtonProps={{ loading: isLoading }}
            autoAdjustOverflow={true}
        >
            <Button loading={isLoading} disabled={!canRevoke} type={'link'}>
                {buttonText}
            </Button>
        </Popconfirm>
    );
}
