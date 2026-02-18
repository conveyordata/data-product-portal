import { DeleteOutlined } from '@ant-design/icons';
import { Avatar, Badge, Button, Space, Table, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { createDataProductIdPath, createOutputPortPath } from '@/types/navigation';
import { type PendingAction, PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { formatDate } from '@/utils/date.helper';

type Props = {
    activeAccess: PendingAction[];
    typeFilter: 'all' | 'outputPort' | 'dataProduct';
    searchTerm: string;
};

type TableRow = {
    key: string;
    pendingAction: PendingAction;
    consumer: { name: string; email: string };
    outputPortName: string;
    dataProductName: string;
    status: 'approved' | 'denied';
    grantedSince: string | null;
    expiresOn: string | null;
};

export function ManageActiveAccessView({ activeAccess, typeFilter, searchTerm }: Props) {
    const { t } = useTranslation();
    const { pagination, handlePaginationChange } = useTablePagination([]);

    // Filter data
    const filteredData = useMemo(() => {
        let filtered = activeAccess;

        // Apply type filter
        if (typeFilter === 'outputPort') {
            filtered = filtered.filter(
                (action) =>
                    action.pending_action_type === PendingActionTypes.DataProductDataset ||
                    action.pending_action_type === PendingActionTypes.DataOutputDataset,
            );
        } else if (typeFilter === 'dataProduct') {
            filtered = filtered.filter(
                (action) =>
                    action.pending_action_type === PendingActionTypes.DataProductRoleAssignment ||
                    action.pending_action_type === PendingActionTypes.DatasetRoleAssignment,
            );
        }

        // Apply search filter
        if (searchTerm) {
            const lowerSearch = searchTerm.toLowerCase();
            filtered = filtered.filter((action) => {
                if (action.pending_action_type === PendingActionTypes.DataProductDataset) {
                    return (
                        action.dataset.name.toLowerCase().includes(lowerSearch) ||
                        action.data_product.name.toLowerCase().includes(lowerSearch) ||
                        action.requested_by.first_name.toLowerCase().includes(lowerSearch) ||
                        action.requested_by.last_name.toLowerCase().includes(lowerSearch) ||
                        action.requested_by.email.toLowerCase().includes(lowerSearch)
                    );
                }
                if (action.pending_action_type === PendingActionTypes.DataOutputDataset) {
                    return (
                        action.dataset.name.toLowerCase().includes(lowerSearch) ||
                        action.data_output.name.toLowerCase().includes(lowerSearch) ||
                        action.requested_by.first_name.toLowerCase().includes(lowerSearch) ||
                        action.requested_by.last_name.toLowerCase().includes(lowerSearch) ||
                        action.requested_by.email.toLowerCase().includes(lowerSearch)
                    );
                }
                return false;
            });
        }

        return filtered;
    }, [activeAccess, typeFilter, searchTerm]);

    // Transform data for table
    const tableData: TableRow[] = useMemo(() => {
        return filteredData.map((action) => {
            if (action.pending_action_type === PendingActionTypes.DataProductDataset) {
                return {
                    key: action.id,
                    pendingAction: action,
                    consumer: {
                        name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                        email: action.requested_by.email,
                    },
                    outputPortName: action.dataset.name,
                    dataProductName: action.data_product.name,
                    status: action.status as 'approved' | 'denied',
                    grantedSince: action.approved_on,
                    expiresOn: null, // Future extension point
                };
            }
            if (action.pending_action_type === PendingActionTypes.DataOutputDataset) {
                return {
                    key: action.id,
                    pendingAction: action,
                    consumer: {
                        name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                        email: action.requested_by.email,
                    },
                    outputPortName: action.dataset.name,
                    dataProductName: action.data_output.name,
                    status: action.status as 'approved' | 'denied',
                    grantedSince: action.approved_on,
                    expiresOn: null,
                };
            }
            // For role assignments, we'll handle them differently when we have that data
            return {
                key: action.id,
                pendingAction: action,
                consumer: { name: '', email: '' },
                outputPortName: '',
                dataProductName: '',
                status: 'approved' as const,
                grantedSince: null,
                expiresOn: null,
            };
        });
    }, [filteredData]);

    const handleRevoke = (_action: PendingAction) => {
        // TODO: Implement revoke functionality
        console.log('Revoke not yet implemented');
    };

    const columns: ColumnsType<TableRow> = [
        {
            title: t('Consumer'),
            dataIndex: 'consumer',
            key: 'consumer',
            render: (consumer: { name: string; email: string }) => (
                <Space>
                    <Avatar style={{ backgroundColor: '#1890ff' }}>
                        {consumer.name
                            .split(' ')
                            .map((n) => n[0])
                            .join('')
                            .toUpperCase()}
                    </Avatar>
                    <div>
                        <div>{consumer.name}</div>
                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                            {consumer.email}
                        </Typography.Text>
                    </div>
                </Space>
            ),
        },
        {
            title: t('Output Port'),
            dataIndex: 'outputPortName',
            key: 'outputPortName',
            render: (outputPortName: string, record: TableRow) => {
                const action = record.pendingAction;
                if (action.pending_action_type === PendingActionTypes.DataProductDataset) {
                    return (
                        <Link
                            to={createOutputPortPath(action.data_product_id, action.dataset_id)}
                            style={{ color: '#1890ff' }}
                        >
                            {outputPortName}
                        </Link>
                    );
                }
                if (action.pending_action_type === PendingActionTypes.DataOutputDataset) {
                    return (
                        <Link
                            to={createOutputPortPath(action.data_output.owner_id, action.dataset_id)}
                            style={{ color: '#1890ff' }}
                        >
                            {outputPortName}
                        </Link>
                    );
                }
                return outputPortName;
            },
        },
        {
            title: t('Data Product'),
            dataIndex: 'dataProductName',
            key: 'dataProductName',
            render: (dataProductName: string, record: TableRow) => {
                const action = record.pendingAction;
                if (action.pending_action_type === PendingActionTypes.DataProductDataset) {
                    return (
                        <Link to={createDataProductIdPath(action.data_product.id)} style={{ color: '#1890ff' }}>
                            {dataProductName}
                        </Link>
                    );
                }
                if (action.pending_action_type === PendingActionTypes.DataOutputDataset) {
                    return (
                        <Link to={createDataProductIdPath(action.data_output.owner_id)} style={{ color: '#1890ff' }}>
                            {dataProductName}
                        </Link>
                    );
                }
                return dataProductName;
            },
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            key: 'status',
            render: (status: 'approved' | 'denied') => {
                if (status === 'approved') {
                    return <Badge status="success" text={t('Approved')} />;
                }
                return <Badge status="error" text={t('Rejected')} />;
            },
        },
        {
            title: t('Granted Since'),
            dataIndex: 'grantedSince',
            key: 'grantedSince',
            render: (grantedSince: string | null) => {
                if (!grantedSince) return '--';
                return formatDate(grantedSince);
            },
        },
        {
            title: t('Expires On'),
            dataIndex: 'expiresOn',
            key: 'expiresOn',
            render: (expiresOn: string | null) => {
                if (!expiresOn) {
                    return <Typography.Text type="secondary">{t('No expiry')}</Typography.Text>;
                }
                return formatDate(expiresOn);
            },
        },
        {
            title: t('Actions'),
            key: 'actions',
            render: (_: unknown, record: TableRow) => {
                if (record.status === 'approved') {
                    return (
                        <Button
                            danger
                            type="text"
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => handleRevoke(record.pendingAction)}
                        >
                            {t('Revoke')}
                        </Button>
                    );
                }
                return '--';
            },
        },
    ];

    return (
        <Table
            columns={columns}
            dataSource={tableData}
            pagination={{
                ...pagination,
                onChange: (page, pageSize) => {
                    handlePaginationChange({ current: page, pageSize });
                },
            }}
            locale={{
                emptyText: t('No active access grants found.'),
            }}
        />
    );
}
