import { DeleteOutlined, ReloadOutlined, StopOutlined } from '@ant-design/icons';
import { Button, Flex, Popconfirm } from 'antd';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS, isExpiringSoon } from '@/components/input-port/access-status.tsx';
import { useGetExpiringSoonThresholdQuery } from '@/store/api/services/generated/accessDurationsApi.ts';
import { InputPortStatus, type OutputPort, RenewalStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

type Props = {
    output_port: OutputPort;
    canRemoveAccess: boolean;
    canRequestAccess: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    handleRenew: (outputPortId: string) => Promise<void>;
    status: InputPortStatus;
    validUntil: string | null;
    renewalStatus?: RenewalStatus | null;
};
export function InputPortActionButton({
    output_port,
    canRemoveAccess,
    canRequestAccess,
    handleRemove,
    handleRenew,
    status,
    validUntil,
    renewalStatus,
}: Props) {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(false);
    const [renewing, setRenewing] = useState(false);
    const { data } = useGetExpiringSoonThresholdQuery();
    const thresholdDays = data?.days ?? DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS;

    const canRenew =
        renewalStatus !== RenewalStatus.Pending &&
        (status === InputPortStatus.Expired || isExpiringSoon(status, validUntil, thresholdDays));

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (datasetId: string, name: string) => {
            try {
                setLoading(true);
                await handleRemove(datasetId);
                dispatchMessage({
                    content:
                        status === InputPortStatus.Pending
                            ? t('Request to link Output Port {{name}} has been cancelled', { name })
                            : t('Output Port {{name}} has been removed', { name }),
                    type: 'success',
                });
            } catch (error) {
                status === InputPortStatus.Pending
                    ? console.error('Failed to cancel Output port link request', error)
                    : console.error('Failed to remove Output port', error);
            }
        },
        [handleRemove, t, status],
    );

    const handleRenewClick = useCallback(async () => {
        try {
            setRenewing(true);
            await handleRenew(output_port.id);
            dispatchMessage({
                content: t('Renewal requested for Output Port {{name}}', { name: output_port.name }),
                type: 'success',
            });
        } catch (error) {
            console.error('Failed to request renewal for Output port', error);
        } finally {
            setRenewing(false);
        }
    }, [handleRenew, output_port.id, output_port.name, t]);

    return (
        <Flex gap={'small'} wrap>
            {canRenew && (
                <Button
                    icon={<ReloadOutlined />}
                    loading={renewing}
                    disabled={!canRequestAccess}
                    type={'link'}
                    onClick={handleRenewClick}
                >
                    {t('Renew')}
                </Button>
            )}
            <Popconfirm
                title={status === InputPortStatus.Pending ? t('Cancel Request') : t('Unlink Output Port')}
                description={
                    status === InputPortStatus.Pending
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
                <Button
                    icon={status === InputPortStatus.Pending ? <StopOutlined /> : <DeleteOutlined />}
                    loading={loading}
                    disabled={!canRemoveAccess}
                    type={'link'}
                >
                    {status === InputPortStatus.Pending ? t('Cancel') : t('Remove')}
                </Button>
            </Popconfirm>
        </Flex>
    );
}
