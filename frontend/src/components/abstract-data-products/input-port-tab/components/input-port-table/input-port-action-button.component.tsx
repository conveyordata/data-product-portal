import { CloseCircleOutlined, ReloadOutlined, StopOutlined } from '@ant-design/icons';
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
    handleCancel: (outputPortId: string) => Promise<void>;
    handleRevoke: (outputPortId: string) => Promise<void>;
    handleRenew: (outputPortId: string) => Promise<void>;
    status: InputPortStatus;
    validUntil: string | null;
    renewalStatus?: RenewalStatus | null;
};
export function InputPortActionButton({
    output_port,
    canRemoveAccess,
    canRequestAccess,
    handleCancel,
    handleRevoke,
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
        (status === InputPortStatus.Expired ||
            status === InputPortStatus.Denied ||
            status === InputPortStatus.Revoked ||
            status === InputPortStatus.Cancelled ||
            isExpiringSoon(status, validUntil, thresholdDays));

    const handleCancelRequest = useCallback(
        async (outputPortId: string, name: string) => {
            try {
                setLoading(true);
                await handleCancel(outputPortId);
                dispatchMessage({
                    content: t('Request to link Output Port {{name}} has been cancelled', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to cancel Output port link request', error);
            } finally {
                setLoading(false);
            }
        },
        [handleCancel, t],
    );

    const handleRevokeAccess = useCallback(
        async (outputPortId: string, name: string) => {
            try {
                setLoading(true);
                await handleRevoke(outputPortId);
                dispatchMessage({
                    content: t('Access to Output Port {{name}} has been revoked', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to revoke access to Output port', error);
            } finally {
                setLoading(false);
            }
        },
        [handleRevoke, t],
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
                    {t('Renew Access')}
                </Button>
            )}
            {(status === InputPortStatus.Pending || renewalStatus === RenewalStatus.Pending) && (
                <Popconfirm
                    title={t('Cancel Request')}
                    description={t('Are you sure you want to cancel the request to link {{name}}?', {
                        name: output_port.name,
                    })}
                    onConfirm={() => handleCancelRequest(output_port.id, output_port.name)}
                    placement={'leftTop'}
                    okText={t('Confirm')}
                    cancelText={t('Cancel')}
                    okButtonProps={{ loading }}
                    autoAdjustOverflow={true}
                >
                    <Button icon={<StopOutlined />} loading={loading} disabled={!canRemoveAccess} type={'link'}>
                        {t('Cancel Request')}
                    </Button>
                </Popconfirm>
            )}
            {status === InputPortStatus.Approved && (
                <Popconfirm
                    title={t('Revoke Access')}
                    description={t('Are you sure you want to revoke access for {{name}}?', {
                        name: output_port.name,
                    })}
                    onConfirm={() => handleRevokeAccess(output_port.id, output_port.name)}
                    placement={'leftTop'}
                    okText={t('Confirm')}
                    cancelText={t('Cancel')}
                    okButtonProps={{ loading }}
                    autoAdjustOverflow={true}
                >
                    <Button icon={<CloseCircleOutlined />} loading={loading} disabled={!canRemoveAccess} type={'link'}>
                        {t('Revoke Access')}
                    </Button>
                </Popconfirm>
            )}
        </Flex>
    );
}
