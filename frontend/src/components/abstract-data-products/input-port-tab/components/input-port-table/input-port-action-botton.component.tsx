import { Button, Flex, Popconfirm } from 'antd';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { InputPortReasoningButton } from '@/components/input-port-reasoning-modal/input-port-reasoning-button.tsx';
import type { OutputPort } from '@/store/api/services/generated/dataProductsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DecisionStatus } from '@/types/roles';

type Props = {
    output_port: OutputPort;
    canRemoveAccess: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    status: DecisionStatus;
    reasoning?: string;
};
export function InputPortActionButton({ output_port, canRemoveAccess, handleRemove, status, reasoning }: Props) {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(false);

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (datasetId: string, name: string) => {
            try {
                setLoading(true);
                await handleRemove(datasetId);
                dispatchMessage({
                    content:
                        status === DecisionStatus.Pending
                            ? t('Request to link Output Port {{name}} has been cancelled', { name })
                            : t('Output Port {{name}} has been removed', { name }),
                    type: 'success',
                });
            } catch (error) {
                status === DecisionStatus.Pending
                    ? console.error('Failed to cancel Output port link request', error)
                    : console.error('Failed to remove Output port', error);
            }
        },
        [handleRemove, t],
    );

    return (
        <Flex gap={'small'}>
            <InputPortReasoningButton reasoning={reasoning} />
            <Popconfirm
                title={status === DecisionStatus.Pending ? t('Cancel Request') : t('Unlink Output Port')}
                description={
                    status === DecisionStatus.Pending
                        ? t('Are you sure you want to cancel the request to link {{name}}?', {
                              name: output_port.name,
                          })
                        : t('Are you sure you want to remove {{name}}?', {
                              name: output_port.name,
                          })
                }
                onConfirm={() => handleRemoveDatasetFromDataProduct(output_port.id, output_port.name)}
                placement={'leftTop'}
                okText={t('Confirm')}
                cancelText={t('Cancel')}
                okButtonProps={{ loading }}
                autoAdjustOverflow={true}
            >
                <Button loading={loading} disabled={!canRemoveAccess} danger>
                    {status === DecisionStatus.Pending ? t('Cancel') : t('Remove')}
                </Button>
            </Popconfirm>
        </Flex>
    );
}
