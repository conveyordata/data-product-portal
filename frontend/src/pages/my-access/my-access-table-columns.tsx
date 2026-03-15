import { DeleteOutlined, RocketOutlined } from '@ant-design/icons';
import { Badge, Button, Flex, Popover, type TableColumnsType, Tag, Tooltip, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type {
    EphemeralAccessPortResponse,
    EphemeralAccessResponse,
} from '@/store/api/services/generated/ephemeralAccessApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';

function ExpiryTag({ expiresAt, status }: { expiresAt: string | null; status: string }) {
    const { t } = useTranslation();

    if (status === 'archived') {
        return <Tag color="default">{t('Archived')}</Tag>;
    }
    if (!expiresAt) {
        return <Tag color="green">{t('No expiry')}</Tag>;
    }

    const now = new Date();
    const expiry = new Date(expiresAt);
    const diffMs = expiry.getTime() - now.getTime();

    if (diffMs <= 0) {
        return <Tag color="red">{t('Expired')}</Tag>;
    }

    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    const label =
        diffHours > 0
            ? t('Expires in {{h}}h {{m}}m', { h: diffHours, m: diffMins })
            : t('Expires in {{m}}m', { m: diffMins });

    return <Tag color={diffHours < 1 ? 'orange' : 'green'}>{label}</Tag>;
}

function portTagColor(status: string): 'success' | 'processing' | 'error' {
    if (status === 'approved') return 'success';
    if (status === 'denied') return 'error';
    return 'processing';
}

function OutputPortTags({ ports }: { ports: EphemeralAccessPortResponse[] }) {
    const { t } = useTranslation();
    return (
        <Flex wrap gap={4}>
            {ports.map((port) =>
                port.status === 'approved' ? (
                    <Link
                        key={port.id}
                        to={createMarketplaceOutputPortPath(port.output_port_id, port.data_product_id)}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <Tag color={portTagColor(port.status)}>{port.output_port_name}</Tag>
                    </Link>
                ) : (
                    <Tooltip
                        key={port.id}
                        title={port.status === 'pending' ? t('Awaiting approval') : t('Access denied')}
                    >
                        <Tag color={portTagColor(port.status)}>{port.output_port_name}</Tag>
                    </Tooltip>
                ),
            )}
        </Flex>
    );
}

export type ActionHandlers = {
    onPromote: (id: string) => void;
    onRevoke: (id: string) => void;
    promotingId: string | null;
    revokingId: string | null;
};

function statusLabel(t: TFunction, status: string, expiresAt: string | null): string {
    if (status === 'archived') return t('Archived');
    if (expiresAt) {
        const diffMs = new Date(expiresAt).getTime() - Date.now();
        if (diffMs <= 0) return t('Expired');
        if (diffMs < 3600_000) return t('Expires soon');
    }
    return t('Active');
}

function badgeStatus(status: string, expiresAt: string | null): 'success' | 'warning' | 'default' {
    if (status === 'archived') return 'default';
    if (expiresAt) {
        const diffMs = new Date(expiresAt).getTime() - Date.now();
        if (diffMs <= 0) return 'default';
        if (diffMs < 3600_000) return 'warning';
    }
    return 'success';
}

export function getMyAccessTableColumns(
    t: TFunction,
    handlers: ActionHandlers,
): TableColumnsType<EphemeralAccessResponse> {
    return [
        {
            title: undefined,
            dataIndex: 'status',
            width: 30,
            render: (status: string, record) => (
                <Popover content={statusLabel(t, status, record.expires_at)} placement="top">
                    <TableCellItem icon={<Badge status={badgeStatus(status, record.expires_at)} />} />
                </Popover>
            ),
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: true,
            render: (name: string) => <TableCellItem text={name} tooltip={{ title: name }} />,
        },
        {
            title: t('Business Question'),
            dataIndex: 'description',
            ellipsis: true,
            render: (description: string) =>
                description ? (
                    <TableCellItem text={description} tooltip={{ title: description }} />
                ) : (
                    <Typography.Text type="secondary">—</Typography.Text>
                ),
        },
        {
            title: t('Expires'),
            dataIndex: 'expires_at',
            width: 160,
            render: (expiresAt: string | null, record) => <ExpiryTag expiresAt={expiresAt} status={record.status} />,
        },
        {
            title: t('Output Ports'),
            dataIndex: 'input_ports',
            render: (ports: EphemeralAccessPortResponse[]) => <OutputPortTags ports={ports} />,
        },
        {
            title: undefined,
            key: 'actions',
            width: 180,
            render: (_: unknown, record) => {
                if (record.status === 'archived') return null;
                return (
                    <Flex gap="small" wrap onClick={(e) => e.stopPropagation()}>
                        <Button
                            icon={<RocketOutlined />}
                            size="small"
                            loading={handlers.promotingId === record.id}
                            onClick={() => handlers.onPromote(record.id)}
                        >
                            {t('Promote')}
                        </Button>
                        <Button
                            danger
                            icon={<DeleteOutlined />}
                            size="small"
                            loading={handlers.revokingId === record.id}
                            onClick={() => handlers.onRevoke(record.id)}
                        >
                            {t('Revoke')}
                        </Button>
                    </Flex>
                );
            },
        },
    ];
}
