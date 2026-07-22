import {
    CalendarOutlined,
    CheckOutlined,
    CloseOutlined,
    FileTextOutlined,
    InfoCircleOutlined,
    UserOutlined,
} from '@ant-design/icons';
import { Avatar, Button, Card, Col, Divider, Flex, Form, Input, Modal, Row, Space, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    AbstractProductIcon,
    DataProductOutlined,
    OutputPortOutlined,
    TechnicalAssetOutlined,
} from '@/components/icons';
import type { AbstractDataProductType } from '@/store/api/services/generated/usersApi.ts';
import {
    type Request,
    RequestType_DataProductRoleAssignment,
    RequestType_InputPort,
    RequestType_TechnicalAssetOutputPort,
} from '@/types/request-types/request-types.tsx';
import { formatDate } from '@/utils/date.helper.ts';

type Props = {
    action?: Request | null;
    open: boolean;
    onClose: () => void;
    onAccept: (action: Request, decisionNote?: string) => void;
    onReject: (action: Request, decisionNote?: string) => void;
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

const abstractDataProductTypeName = (type: AbstractDataProductType) => {
    switch (type) {
        case 'data_products':
            return 'Data Product';
        case 'explorations':
            return 'Exploration';
        default:
            return '';
    }
};

function getRequestDetails(
    action: Request,
    t: (key: string, params?: Record<string, string>) => string,
): RequestDetails | undefined {
    if (action.request_type === RequestType_InputPort) {
        return {
            requesterName: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
            requesterEmail: action.requested_by.email,
            requestType: t('Output Port Access'),
            source: {
                name: action.input_port.consuming_abstract_data_product.name,
                email: action.requested_by.email,
                type: t(
                    abstractDataProductTypeName(
                        action.input_port.consuming_abstract_data_product.abstract_data_product_type,
                    ),
                ),
                icon: (
                    <AbstractProductIcon
                        type={action.input_port.consuming_abstract_data_product.abstract_data_product_type}
                    />
                ),
            },
            target: {
                name: action.input_port.output_port.name,
                type: t('Output Port'),
                icon: <OutputPortOutlined />,
            },
            accessType: t('READ ONLY'),
            justification: action.justification || t('No justification provided'),
            hasJustification: true,
            requestedOn: action.requested_on,
            title: t('Review Output Port Access Request'),
        };
    }

    if (action.request_type === RequestType_TechnicalAssetOutputPort) {
        return {
            requesterName: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
            requesterEmail: action.requested_by.email,
            requestType: t('Technical Asset Inclusion'),
            source: {
                name: action.technical_asset.name,
                email: action.requested_by.email,
                type: t('Technical Asset'),
                icon: <TechnicalAssetOutlined />,
            },
            target: {
                name: action.output_port.name,
                type: t('Output Port'),
                icon: <OutputPortOutlined />,
            },
            accessType: t('INCLUDE'),
            justification: '',
            hasJustification: false,
            requestedOn: action.requested_on,
            title: t('Review Technical Asset Request'),
        };
    }

    if (action.request_type === RequestType_DataProductRoleAssignment) {
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
    const [form] = Form.useForm<{ decisionNote: string }>();
    const [isAccepting, setIsAccepting] = useState(false);

    if (!action) {
        return null;
    }

    const details = getRequestDetails(action, t);

    const handleAccept = () => {
        const { decisionNote } = form.getFieldsValue();
        onAccept(action, decisionNote);
        onClose();
        form.resetFields();
    };

    const handleReject = () => {
        const { decisionNote } = form.getFieldsValue();
        if (action.request_type === RequestType_InputPort && !decisionNote?.trim()) {
            form.setFields([{ name: 'decisionNote', errors: [t('A decision note is required when declining')] }]);
            return;
        }
        setIsAccepting(true);
        onReject(action, decisionNote);
        onClose();
        form.resetFields();
        setIsAccepting(false);
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
                    <Button danger icon={<CloseOutlined />} loading={isAccepting} onClick={handleReject}>
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
                                        <Typography.Text>{details.justification}</Typography.Text>
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
                {action.request_type === RequestType_InputPort && (
                    <Col span={24}>
                        <Form form={form} layout="vertical">
                            <Form.Item
                                name="decisionNote"
                                label={t('Decision note')}
                                extra={t('Required when declining, optional when accepting')}
                            >
                                <Input.TextArea
                                    rows={3}
                                    onChange={() => form.setFields([{ name: 'decisionNote', errors: [] }])}
                                />
                            </Form.Item>
                        </Form>
                    </Col>
                )}
            </Row>
        </Modal>
    );
}
