import {
    ArrowRightOutlined,
    CalendarOutlined,
    CheckOutlined,
    CloseOutlined,
    DeploymentUnitOutlined,
    FileTextOutlined,
    InfoCircleOutlined,
    LockOutlined,
    ProductOutlined,
    ToolOutlined,
    UserOutlined,
} from '@ant-design/icons';
import { Alert, Button, Card, Divider, Flex, Modal, Space, Tag, Typography } from 'antd';
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

type RequestDetails = {
    requesterName: string;
    requesterEmail: string;
    requestType: string;
    source: {
        name: string;
        type: string;
        icon: React.ReactNode;
        badge?: string;
    };
    target: {
        name: string;
        type: string;
        icon: React.ReactNode;
        badge: string;
    };
    accessType: string;
    justification: string;
    hasJustification: boolean;
    requestedOn: string;
    title: string;
};

function getRequestDetails(
    action: PendingAction,
    t: (key: string, params?: Record<string, string>) => string,
): RequestDetails {
    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return {
            requesterName: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
            requesterEmail: action.requested_by.email,
            requestType: t('Output Port Access'),
            source: {
                name: action.data_product.name,
                type: t('Data Product'),
                icon: <ProductOutlined />,
                badge: t('Requesting Access'),
            },
            target: {
                name: action.output_port.name,
                type: t('Output Port'),
                icon: <DeploymentUnitOutlined />,
                badge: t('Your Resource'),
            },
            accessType: t('READ ACCESS'),
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
            source: {
                name: action.technical_asset.name,
                type: t('Technical Asset'),
                icon: <ToolOutlined />,
                badge: t('Requesting Inclusion'),
            },
            target: {
                name: action.output_port.name,
                type: t('Output Port'),
                icon: <DeploymentUnitOutlined />,
                badge: t('Your Resource'),
            },
            accessType: t('INCLUDE'),
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
            source: {
                name: `${action.user.first_name} ${action.user.last_name}`,
                type: t('User'),
                icon: <UserOutlined />,
                badge: t('Requesting Role'),
            },
            target: {
                name: action.data_product.name,
                type: t('Data Product'),
                icon: <ProductOutlined />,
                badge: t('Your Resource'),
            },
            accessType: t('ROLE: {{roleName}}', { roleName: roleName.toUpperCase() }),
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
        source: {
            name: '',
            type: '',
            icon: null,
        },
        target: {
            name: '',
            type: '',
            icon: null,
            badge: '',
        },
        accessType: '',
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
            <Flex vertical gap="middle">
                {/* Access Flow Visualization */}
                <div>
                    <Typography.Title level={5}>
                        <LockOutlined /> {t('Access Flow')}
                    </Typography.Title>
                    <Alert
                        title={t('Review carefully: You are granting access to your resource listed on the right.')}
                        type="warning"
                        showIcon
                    />
                </div>
                <Flex align="center" justify="space-between" gap="middle">
                    {/* Source Card - Thing Requesting Access */}
                    <Card size="small" className={styles.accessCard} variant="outlined">
                        <Flex vertical gap="small">
                            {details.source.badge && <Tag>{details.source.badge}</Tag>}
                            <Flex align="center" gap="middle">
                                <div className={styles.iconContainer}>{details.source.icon}</div>
                                <Flex vertical>
                                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                        {details.source.type}
                                    </Typography.Text>
                                    <Typography.Text strong>{details.source.name}</Typography.Text>
                                </Flex>
                            </Flex>
                        </Flex>
                    </Card>

                    {/* Arrow with Access Type */}
                    <Flex vertical align="center" gap="small">
                        <ArrowRightOutlined style={{ fontSize: 28 }} />
                        <Tag>{details.accessType}</Tag>
                    </Flex>

                    {/* Target Card - Your Controlled Resource */}
                    <Card size="small" className={styles.accessCard} variant="outlined">
                        <Flex vertical gap="small">
                            <Tag>{details.target.badge}</Tag>
                            <Flex align="center" gap="middle">
                                <div className={styles.iconContainer}>{details.target.icon}</div>
                                <Flex vertical flex={1}>
                                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                        {details.target.type}
                                    </Typography.Text>
                                    <Typography.Text strong>{details.target.name}</Typography.Text>
                                </Flex>
                            </Flex>
                        </Flex>
                    </Card>
                </Flex>

                {/* Request Details */}
                <div>
                    <Typography.Title level={5}>
                        <InfoCircleOutlined /> {t('Request Details')}
                    </Typography.Title>
                    <Card size="small" className={styles.detailCard} variant="outlined">
                        <Flex vertical gap="middle">
                            <Flex justify="space-between" gap="large">
                                <Flex align="center" gap="middle">
                                    <div className={styles.detailIconContainer}>
                                        <UserOutlined />
                                    </div>
                                    <Flex vertical>
                                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                            {t('Requested By')}
                                        </Typography.Text>
                                        <Typography.Text strong>{details.requesterName}</Typography.Text>
                                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                            {details.requesterEmail}
                                        </Typography.Text>
                                    </Flex>
                                </Flex>

                                <Flex align="center" gap="middle">
                                    <div className={styles.detailIconContainer}>
                                        <CalendarOutlined />
                                    </div>
                                    <Flex vertical>
                                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                            {t('Requested On')}
                                        </Typography.Text>
                                        <Typography.Text strong>{formatDate(details.requestedOn)}</Typography.Text>
                                    </Flex>
                                </Flex>
                            </Flex>

                            {details.hasJustification && (
                                <>
                                    <Divider style={{ margin: 0 }} />
                                    <Flex vertical gap="small">
                                        <Flex gap="small">
                                            <FileTextOutlined />
                                            <Typography.Text strong>{t('Business Justification')}</Typography.Text>
                                        </Flex>
                                        <div className={styles.justificationContainer}>
                                            <Typography.Text>{details.justification}</Typography.Text>
                                        </div>
                                    </Flex>
                                </>
                            )}
                        </Flex>
                    </Card>
                </div>
            </Flex>
        </Modal>
    );
}
