import { CheckOutlined, CloseOutlined, UserOutlined } from '@ant-design/icons';
import {
    Avatar,
    Badge,
    Button,
    Card,
    Descriptions,
    type DescriptionsProps,
    Flex,
    Form,
    Input,
    Modal,
    Typography,
    theme,
} from 'antd';
import { addDays } from 'date-fns';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    AbstractProductIcon,
    DataProductOutlined,
    OutputPortOutlined,
    TechnicalAssetOutlined,
} from '@/components/icons';
import { AccessDurationType } from '@/store/api/services/generated/configurationAccessDurationsApi.ts';
import { InputPortStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { RenewalStatus } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import type { AbstractDataProductType } from '@/store/api/services/generated/usersApi.ts';
import {
    type Request,
    RequestType_DataProductRoleAssignment,
    RequestType_InputPort,
    RequestType_TechnicalAssetOutputPort,
} from '@/types/request-types/request-types.tsx';
import { formatDate } from '@/utils/date.helper.ts';
import { getInputPortStatusBadgeStatus, getInputPortStatusLabel } from '@/utils/status.helper.ts';

type Props = {
    action?: Request | null;
    open: boolean;
    onClose: () => void;
    onAccept?: (action: Request, decisionNote?: string) => void;
    onReject?: (action: Request, decisionNote?: string) => void;
    readOnly?: boolean;
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
    accessDurationDays?: number | null;
    isPermanent?: boolean;
    renewalStatus?: string | null;
    currentAccessPeriod?: {
        label: string;
        wasRevoked: boolean;
        validUntil: string | null;
    } | null;
};

function formatAccessPeriodLabel(
    t: (key: string) => string,
    current: {
        valid_from?: string | null;
        valid_until: string | null;
        access_duration_type: 'permanent' | 'time_bound';
    },
): string {
    if (current.access_duration_type === 'permanent') {
        return t('Permanent');
    }
    if (current.valid_from && current.valid_until) {
        return `${formatDate(current.valid_from)} - ${formatDate(current.valid_until)}`;
    }
    if (current.valid_until) {
        return `${t('Until')} ${formatDate(current.valid_until)}`;
    }
    return t('Unknown');
}

function getPreviousRequestStatus(period: { wasRevoked: boolean; validUntil: string | null }): InputPortStatus {
    if (period.wasRevoked) {
        return InputPortStatus.Revoked;
    }
    if (period.validUntil && new Date(period.validUntil) < new Date()) {
        return InputPortStatus.Expired;
    }
    return InputPortStatus.Approved;
}

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
            accessDurationDays: action.requested_duration_days,
            isPermanent: action.access_duration_type === AccessDurationType.Permanent,
            renewalStatus: action.input_port.renewal_status,
            currentAccessPeriod:
                action.input_port.current_request.id !== action.id
                    ? {
                          label: formatAccessPeriodLabel(t, action.input_port.current_request),
                          wasRevoked: action.input_port.current_request.revoked_at != null,
                          validUntil: action.input_port.current_request.valid_until,
                      }
                    : null,
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

export function ReviewRequestModal({ action, open, onClose, onAccept, onReject, readOnly = false }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const tileLabelStyle = { fontSize: token.fontSizeSM, textTransform: 'uppercase' as const };
    const [form] = Form.useForm<{ decisionNote: string }>();
    const [isAccepting, setIsAccepting] = useState(false);
    const [showPreviousRequest, setShowPreviousRequest] = useState(false);

    if (!action) {
        return null;
    }

    const details = getRequestDetails(action, t);

    const handleAccept = () => {
        const { decisionNote } = form.getFieldsValue();
        onAccept?.(action, decisionNote);
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
        onReject?.(action, decisionNote);
        onClose();
        form.resetFields();
        setIsAccepting(false);
    };

    if (!details) return null;

    const previousRequestAction: Request | null =
        action.request_type === RequestType_InputPort && details.currentAccessPeriod
            ? {
                  ...action.input_port.current_request,
                  request_type: RequestType_InputPort,
                  input_port: { ...action.input_port, renewal_status: null },
              }
            : null;

    const previousRequestStatus = details.currentAccessPeriod
        ? getPreviousRequestStatus(details.currentAccessPeriod)
        : null;

    const detailItems: DescriptionsProps['items'] = [
        ...(details.hasJustification
            ? [
                  {
                      key: 'justification',
                      label: t('Business Justification'),
                      span: 2,
                      children: details.justification,
                  },
              ]
            : []),
        {
            key: 'requested-on',
            label: t('Requested On'),
            children: formatDate(details.requestedOn),
        },
        {
            key: 'requested-by',
            label: t('Requested By'),
            children: (
                <Flex align="baseline" gap="small" wrap>
                    <Typography.Text>{details.requesterName}</Typography.Text>
                    <Typography.Text type="secondary" style={{ fontSize: token.fontSizeSM }}>
                        {details.requesterEmail}
                    </Typography.Text>
                </Flex>
            ),
        },
        ...(details.isPermanent === true || (details.isPermanent === false && details.accessDurationDays != null)
            ? [
                  {
                      key: 'requested-duration',
                      label: t('Requested Duration'),
                      children: details.isPermanent ? t('Permanent') : `${details.accessDurationDays} ${t('days')}`,
                  },
                  ...(!details.isPermanent && details.accessDurationDays != null
                      ? [
                            {
                                key: 'calculated-end-date',
                                label: t('Calculated End Date'),
                                children: formatDate(addDays(new Date(), details.accessDurationDays)),
                            },
                        ]
                      : []),
              ]
            : []),
    ];

    return (
        <>
            <Modal
                title={
                    <Flex vertical>
                        {details.renewalStatus === RenewalStatus.Pending && (
                            <Typography.Text
                                strong
                                style={{
                                    color: token.colorPrimary,
                                    fontSize: token.fontSizeSM,
                                    textTransform: 'uppercase',
                                }}
                            >
                                {t('Renewal')}
                            </Typography.Text>
                        )}
                        <span>{readOnly ? t('Previous Request') : details.title}</span>
                    </Flex>
                }
                open={open}
                onCancel={onClose}
                width={800}
                footer={
                    readOnly ? null : (
                        <Flex gap="small" justify="flex-end">
                            <Button danger icon={<CloseOutlined />} loading={isAccepting} onClick={handleReject}>
                                {t('Decline')}
                            </Button>
                            <Button type="primary" icon={<CheckOutlined />} onClick={handleAccept}>
                                {t('Accept')}
                            </Button>
                        </Flex>
                    )
                }
            >
                <Flex vertical gap="middle">
                    <Flex gap="small" align="stretch">
                        <Card size="small" variant="outlined" style={{ flex: 3 }}>
                            <Flex vertical gap="small">
                                <Typography.Text type="secondary" style={tileLabelStyle}>
                                    {t('Requesting Consumer')}
                                </Typography.Text>
                                <Flex align="center" gap="small">
                                    <Avatar
                                        icon={details.source.icon}
                                        style={{ color: token.colorPrimary, backgroundColor: token.colorPrimaryBg }}
                                    />
                                    <Typography.Text strong>{details.source.name}</Typography.Text>
                                </Flex>
                            </Flex>
                        </Card>
                        <Card size="small" variant="outlined" style={{ flex: 2 }}>
                            <Flex vertical gap="small">
                                <Typography.Text type="secondary" style={tileLabelStyle}>
                                    {details.requestType === t('Role Assignment')
                                        ? t('Requests Role')
                                        : t('Requests Access')}
                                </Typography.Text>
                                <Typography.Text strong>{details.accessType}</Typography.Text>
                            </Flex>
                        </Card>
                        <Card size="small" variant="outlined" style={{ flex: 3 }}>
                            <Flex vertical gap="small">
                                <Typography.Text type="secondary" style={tileLabelStyle}>
                                    {t('Requested Resource')}
                                </Typography.Text>
                                <Flex align="center" gap="small">
                                    <Avatar
                                        icon={details.target.icon}
                                        style={{ color: token.colorPrimary, backgroundColor: token.colorPrimaryBg }}
                                    />
                                    <Flex vertical>
                                        <Typography.Text strong>{details.target.name}</Typography.Text>
                                        {details.target.type && (
                                            <Typography.Text type="secondary" style={{ fontSize: token.fontSizeSM }}>
                                                {details.target.type}
                                            </Typography.Text>
                                        )}
                                    </Flex>
                                </Flex>
                            </Flex>
                        </Card>
                    </Flex>

                    <Card size="small" variant="outlined" title={t('Request Details')}>
                        <Descriptions
                            column={2}
                            layout="vertical"
                            size="small"
                            items={detailItems}
                            styles={{ label: { color: token.colorTextSecondary } }}
                        />
                    </Card>

                    {details.currentAccessPeriod && (
                        <Card
                            size="small"
                            variant="outlined"
                            title={
                                <Flex align="center" justify="space-between">
                                    <span>{t('Previous Request')}</span>
                                    {previousRequestStatus && (
                                        <Badge
                                            status={getInputPortStatusBadgeStatus(previousRequestStatus)}
                                            text={getInputPortStatusLabel(t, previousRequestStatus)}
                                        />
                                    )}
                                </Flex>
                            }
                            hoverable={!!previousRequestAction}
                            onClick={previousRequestAction ? () => setShowPreviousRequest(true) : undefined}
                        >
                            <Typography.Text>{details.currentAccessPeriod.label}</Typography.Text>
                        </Card>
                    )}

                    {!readOnly && action.request_type === RequestType_InputPort && (
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
                    )}
                </Flex>
            </Modal>
            {previousRequestAction && (
                <ReviewRequestModal
                    action={previousRequestAction}
                    open={showPreviousRequest}
                    onClose={() => setShowPreviousRequest(false)}
                    readOnly
                />
            )}
        </>
    );
}
