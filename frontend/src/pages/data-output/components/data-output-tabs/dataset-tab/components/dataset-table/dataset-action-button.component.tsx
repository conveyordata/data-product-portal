import { Button, Popconfirm } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type { OutputPort } from '@/store/api/services/generated/usersApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useRemoveDatasetFromDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DecisionStatus } from '@/types/roles';

type Props = {
    outputPort: OutputPort;
    technicalAssetIt: string;
    dataProductId: string | undefined;
    status: DecisionStatus;
};
export function DatasetActionButton({ outputPort, technicalAssetIt, dataProductId, status }: Props) {
    const { t } = useTranslation();

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
        },
        { skip: !dataProductId },
    );
    const canRevoke = access?.allowed ?? false;

    const [removeDatasetFromDataOutput, { isLoading }] = useRemoveDatasetFromDataOutputMutation();

    const handleRemoveDatasetFromDataOutput = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataOutput({ datasetId, dataOutputId: technicalAssetIt }).unwrap();
                dispatchMessage({
                    content: t('Output Port {{name}} has been removed from Technical Asset', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove dataset from Technical Asset', error);
            }
        },
        [technicalAssetIt, removeDatasetFromDataOutput, t],
    );

    const handleCancelDatasetLinkRequest = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataOutput({ datasetId, dataOutputId: technicalAssetIt }).unwrap();
                dispatchMessage({
                    content: t('Request to link Output Port {{name}} has been cancelled', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to cancel dataset link request', error);
            }
        },
        [technicalAssetIt, removeDatasetFromDataOutput, t],
    );

    const buttonText = status === DecisionStatus.Pending ? t('Cancel') : t('Remove');
    const popupTitle = status === DecisionStatus.Pending ? t('Cancel Request') : t('Unlink Output Port');
    const popupDescription =
        status === DecisionStatus.Pending
            ? t('Are you sure you want to cancel the request to link {{name}} to the Technical Asset?', {
                  name: outputPort.name,
              })
            : t('Are you sure you want to remove {{name}} from the Technical Asset?', {
                  name: outputPort.name,
              });
    const onConfirm =
        status === DecisionStatus.Pending ? handleCancelDatasetLinkRequest : handleRemoveDatasetFromDataOutput;

    return (
        <Popconfirm
            title={popupTitle}
            description={popupDescription}
            onConfirm={() => onConfirm(outputPort.id, outputPort.name)}
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
