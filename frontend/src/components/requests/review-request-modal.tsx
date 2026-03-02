import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Descriptions, Flex, Modal, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';
import { formatDate } from '@/utils/date.helper';
import styles from './requests.module.scss';

type Props = {
    action: PendingAction | null;
    open: boolean;
    onClose: () => void;
    onAccept: (action: PendingAction) => void;
    onReject: (action: PendingAction) => void;
};

function getRequestDetails(action: PendingAction, t: (key: string, params?: Record<string, string>) => string) {
    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return {
            requesterName: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
            requesterEmail: action.requested_by.email,
            requestType: t('Output Port Access'),
            requestSummary: t(
                'The Data Product {{dataProductName}} is requesting read access to the Output Port {{outputPortName}}.',
                {
                    dataProductName: action.data_product.name,
                    outputPortName: action.output_port.name,
                },
            ),
            source: action.data_product.name,
            target: action.output_port.name,
            justification: action.justification || t('No justification provided'),
            hasJustification: true,
            requestedOn: action.requested_on,
            title: t('Review Output Port Access Request'),
        };
    }

    if (action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort) {
        return {
            requesterName: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
            requesterEmail: action.requested_by.email,
            requestType: t('Technical Asset Inclusion'),
            requestSummary: t(
                'The Technical Asset {{assetName}} is requesting to be included in the Output Port {{outputPortName}}.',
                {
                    assetName: action.technical_asset.name,
                    outputPortName: action.output_port.name,
                },
            ),
            source: action.technical_asset.name,
            target: action.output_port.name,
            justification: '',
            hasJustification: false,
            requestedOn: action.requested_on,
            title: t('Review Technical Asset Request'),
        };
    }

    if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
        const roleName = action.role ? action.role.name : t('a role');
        return {
            requesterName: `${action.user.first_name} ${action.user.last_name}`,
            requesterEmail: action.user.email,
            requestType: t('Role Assignment'),
            requestSummary: t(
                '{{userName}} is requesting the {{roleName}} role on the Data Product {{dataProductName}}.',
                {
                    userName: `${action.user.first_name} ${action.user.last_name}`,
                    roleName,
                    dataProductName: action.data_product.name,
                },
            ),
            source: `${action.user.first_name} ${action.user.last_name}`,
            target: action.data_product.name,
            justification: '',
            hasJustification: false,
            requestedOn: action.requested_on || '',
            title: t('Review Role Assignment Request'),
        };
    }

    return {
        requesterName: '',
        requesterEmail: '',
        requestType: '',
        requestSummary: '',
        source: '',
        target: '',
        justification: '',
        hasJustification: false,
        requestedOn: '',
        title: t('Review Request'),
    };
}

export function ReviewRequestModal({ action, open, onClose, onAccept, onReject }: Props) {
    const { t } = useTranslation();

    if (!action) return null;

    const details = getRequestDetails(action, t);

    const handleAccept = () => {
        onAccept(action);
        onClose();
    };

    const handleReject = () => {
        onReject(action);
        onClose();
    };

    return (
        <Modal
            title={details.title}
            open={open}
            onCancel={onClose}
            width={700}
            footer={
                <Space>
                    <Button onClick={onClose}>{t('Cancel')}</Button>
                    <Button danger icon={<CloseOutlined />} onClick={handleReject}>
                        {t('Decline')}
                    </Button>
                    <Button type="primary" icon={<CheckOutlined />} onClick={handleAccept}>
                        {t('Accept')}
                    </Button>
                </Space>
            }
        >
            <Space orientation="vertical" size="large">
                <Typography.Paragraph>{details.requestSummary}</Typography.Paragraph>
                <Descriptions bordered column={1} size="small">
                    <Descriptions.Item label={t('Request Type')}>{details.requestType}</Descriptions.Item>
                    <Descriptions.Item label={t('Requested By')}>
                        <Flex vertical>
                            <Typography.Text>{details.requesterName}</Typography.Text>
                            <Typography.Text type="secondary">{details.requesterEmail}</Typography.Text>
                        </Flex>
                    </Descriptions.Item>
                    <Descriptions.Item label={t('Requested On')}>{formatDate(details.requestedOn)}</Descriptions.Item>
                    <Descriptions.Item label={t('Source')}>{details.source}</Descriptions.Item>
                    <Descriptions.Item label={t('Target')}>{details.target}</Descriptions.Item>
                </Descriptions>

                {details.hasJustification && (
                    <Flex vertical>
                        <Typography.Title level={5}>{t('Business Justification')}</Typography.Title>
                        <Flex className={styles.justificationContainer}>
                            <Typography.Paragraph style={{ marginBottom: 0 }}>
                                {details.justification}
                            </Typography.Paragraph>
                        </Flex>
                    </Flex>
                )}
            </Space>
        </Modal>
    );
}
