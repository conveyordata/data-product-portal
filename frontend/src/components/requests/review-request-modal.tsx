import {
    CalendarOutlined,
    CheckOutlined,
    CloseOutlined,
    FileTextOutlined,
    InfoCircleOutlined,
    UserOutlined,
} from '@ant-design/icons';
import { Avatar, Button, Card, Col, Divider, Flex, Modal, Row, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';
import { formatDate } from '@/utils/date.helper';
import { DataOutputOutlined, DataProductOutlined, DatasetOutlined } from '../icons';

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
        email: string;
        type: string;
        icon: React.ReactNode;
        badge?: string;
    };
    target: {
        name: string;
        type: string;
        icon: React.ReactNode;
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
): RequestDetails | undefined {
    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return {
            requesterName: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
            requesterEmail: action.requested_by.email,
            requestType: t('Output Port Access'),
            source: {
                name: action.data_product.name,
                email: action.requested_by.email,
                type: t('Data Product'),
                icon: <DataProductOutlined />,
            },
            target: {
                name: action.output_port.name,
                type: t('Output Port'),
                icon: <DatasetOutlined />,
            },
            accessType: t('READ ONLY'),
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
                email: action.requested_by.email,
                type: t('Technical Asset'),
                icon: <DataOutputOutlined />,
            },
            target: {
                name: action.output_port.name,
                type: t('Output Port'),
                icon: <DatasetOutlined />,
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
            requesterName: `${action.requested_by?.first_name} ${action.requested_by?.last_name}`,
            requesterEmail: action.requested_by?.email || '',
            requestType: t('Role Assignment'),
            source: {
                name: `${action.user.first_name} ${action.user.last_name}`,
                email: action.user.email,
                type: t('User'),
                icon: <UserOutlined />,
            },
            target: {
                name: action.data_product.name,
                type: t('Data Product'),
                icon: <DataProductOutlined />,
            },
            accessType: roleName,
            justification: '',
            hasJustification: false,
            requestedOn: action.requested_on || '',
            title: t('Review Role Assignment Request'),
        };
    }

    return undefined;
}

export function ReviewRequestModal({ action, open, onClose, onAccept, onReject }: Props) {
    const { t } = useTranslation();

    if (!action) {
        // throw exception
        return null;
        // throw new Error('ReviewRequestModal opened without a pending action');
    }

    const details = getRequestDetails(action, t);

    const handleAccept = () => {
        onAccept(action);
        onClose();
    };

    const handleReject = () => {
        onReject(action);
        onClose();
    };

    if (!details) return null;

    return (
        <Modal
            title={details.title}
            open={open}
            onCancel={onClose}
            width={800}
            footer={
                <Space>
                    <Button danger icon={<CloseOutlined />} onClick={handleReject}>
                        {t('Decline')}
                    </Button>
                    <Button type="primary" icon={<CheckOutlined />} onClick={handleAccept}>
                        {t('Accept')}
                    </Button>
                </Space>
            }
        >
            {/* 3-Tile Access Visualization using Antd Row/Col */}
            <Row gutter={[16, 16]}>
                {/* Requesting Consumer Tile */}
                <Col span={9}>
                    <Card size="small" variant="outlined">
                        <Typography.Text strong style={{ fontSize: 12 }}>
                            {t('Requesting Consumer')}
                        </Typography.Text>
                        <Flex align="center" gap="middle">
                            <Avatar
                                icon={details.source.icon}
                                style={{ color: '#1890ff', backgroundColor: '#e6f7ff' }}
                            />
                            <Flex vertical>
                                <Typography.Text strong>{details.source.name}</Typography.Text>
                                {details.source.email && (
                                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                        {details.source.email}
                                    </Typography.Text>
                                )}
                            </Flex>
                        </Flex>
                    </Card>
                </Col>
                {/* Requests Role/Access Tile (smaller) */}
                <Col span={6} style={{ display: 'flex' }}>
                    <Card size="small" variant="outlined" style={{ flex: 1 }}>
                        <Typography.Text strong style={{ fontSize: 12 }}>
                            {details.requestType === t('Role Assignment') ? t('Requests Role') : t('Requests Access')}
                        </Typography.Text>
                        <Flex align="center" justify="center">
                            <Typography.Text strong style={{ fontSize: 16 }}>
                                {details.accessType}
                            </Typography.Text>
                        </Flex>
                    </Card>
                </Col>
                {/* Requested Resource Tile */}
                <Col span={9}>
                    <Card size="small" variant="outlined">
                        <Typography.Text strong style={{ fontSize: 12 }}>
                            {t('Requested Resource')}
                        </Typography.Text>
                        <Flex align="center" gap="middle">
                            <Avatar
                                icon={details.target.icon}
                                style={{ color: '#1890ff', backgroundColor: '#e6f7ff' }}
                            />
                            <Flex vertical>
                                <Typography.Text strong>{details.target.name}</Typography.Text>
                                {details.target.type && (
                                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                        {details.target.type}
                                    </Typography.Text>
                                )}
                            </Flex>
                        </Flex>
                    </Card>
                </Col>

                {/* Request Details */}
                <Col span={24}>
                    <Typography.Title level={5}>
                        <InfoCircleOutlined /> {t('Request Details')}
                    </Typography.Title>
                    <Card size="small" variant="outlined">
                        <Flex vertical gap="middle">
                            {details.hasJustification && (
                                <>
                                    <Flex vertical gap="small">
                                        <Flex gap="small">
                                            <FileTextOutlined />
                                            <Typography.Text strong>{t('Business Justification')}</Typography.Text>
                                        </Flex>
                                        <Typography.Text code>{details.justification}</Typography.Text>
                                    </Flex>
                                    <Divider style={{ margin: 0 }} />
                                </>
                            )}
                            <Flex justify="space-between" gap="large">
                                <Flex align="center" gap="middle">
                                    <Avatar
                                        icon={<UserOutlined />}
                                        style={{ color: '#1890ff', backgroundColor: '#e6f7ff' }}
                                    />
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
                                    <Avatar
                                        icon={<CalendarOutlined />}
                                        style={{ color: '#1890ff', backgroundColor: '#e6f7ff' }}
                                    />
                                    <Flex vertical>
                                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                            {t('Requested On')}
                                        </Typography.Text>
                                        <Typography.Text strong>{formatDate(details.requestedOn)}</Typography.Text>
                                    </Flex>
                                </Flex>
                            </Flex>
                        </Flex>
                    </Card>
                </Col>
            </Row>
        </Modal>
    );
}
