import { Button, Popconfirm } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type OutputPort,
    useUnlinkInputPortFromDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { DecisionStatus } from '@/types/roles';

type Props = {
    output_port: OutputPort;
    dataProductId: string;
    status: DecisionStatus;
};
export function InputPortActionButton({ output_port, dataProductId, status }: Props) {
    const { t } = useTranslation();

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
        },
        { skip: !dataProductId },
    );
    const canRevoke = access?.allowed ?? false;

    const [removeDatasetFromDataProduct, { isLoading }] = useUnlinkInputPortFromDataProductMutation();

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataProduct({ inputPortId: datasetId, id: dataProductId }).unwrap();
                dispatchMessage({
                    content: t('Output Port {{name}} has been removed from Data Product', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove dataset from Data Product', error);
            }
        },
        [dataProductId, removeDatasetFromDataProduct, t],
    );

    const handleCancelDatasetLinkRequest = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataProduct({ inputPortId: datasetId, id: dataProductId }).unwrap();
                dispatchMessage({
                    content: t('Request to link Output Port {{name}} has been cancelled', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to cancel dataset link request', error);
            }
        },
        [dataProductId, removeDatasetFromDataProduct, t],
    );

    const buttonText = status === DecisionStatus.Pending ? t('Cancel') : t('Remove');
    const popupTitle = status === DecisionStatus.Pending ? t('Cancel Request') : t('Unlink Output Port');
    const popupDescription =
        status === DecisionStatus.Pending
            ? t('Are you sure you want to cancel the request to link {{name}} to the Data Product?', {
                  name: output_port.name,
              })
            : t('Are you sure you want to remove {{name}} from the Data Product?', {
                  name: output_port.name,
              });
    const onConfirm =
        status === DecisionStatus.Pending ? handleCancelDatasetLinkRequest : handleRemoveDatasetFromDataProduct;

    return (
        <Popconfirm
            title={popupTitle}
            description={popupDescription}
            onConfirm={() => onConfirm(output_port.id, output_port.name)}
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
