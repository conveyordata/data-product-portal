import { InboxOutlined, SearchOutlined } from '@ant-design/icons';
import { Divider, Flex, Input, Segmented, Space } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi';
import { PendingAccessRequestsView } from './pending-access-requests-view';

type ViewMode = 'pending' | 'active';
type TypeFilter = 'all' | 'outputPort' | 'dataProduct';

export function RequestsPanel() {
    const { t } = useTranslation();
    const [viewMode, setViewMode] = useState<ViewMode>('pending');
    const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
    const [searchTerm, setSearchTerm] = useState('');

    const { data: { pending_actions } = {} } = useGetUserPendingActionsQuery();

    // Filter pending requests
    const pendingRequests = useMemo(() => {
        if (!pending_actions) return [];
        return pending_actions;
    }, [pending_actions]);

    // Get counts for badges
    const pendingCount = pendingRequests.length;

    // View mode segmented control options
    const viewModeOptions = [
        {
            label: (
                <Space size="small">
                    <InboxOutlined style={{ fontSize: 16 }} />
                    {t('Pending Access Requests')}
                    {pendingCount > 0 && <span>({pendingCount})</span>}
                </Space>
            ),
            value: 'pending' as ViewMode,
        },
    ];

    // Type filter segmented control options
    const typeFilterOptions = [
        {
            label: t('All'),
            value: 'all' as TypeFilter,
        },
        {
            label: (
                <Space size="small">
                    <DatasetOutlined style={{ fontSize: 14 }} />
                    {t('Output Port')}
                </Space>
            ),
            value: 'outputPort' as TypeFilter,
        },
        {
            label: (
                <Space size="small">
                    <DataProductOutlined style={{ fontSize: 14 }} />
                    {t('Data Product')}
                </Space>
            ),
            value: 'dataProduct' as TypeFilter,
        },
    ];

    return (
        <div>
            {/* Toolbar with segmented controls and search */}
            <Flex gap="middle" align="center" style={{ marginBottom: 16 }}>
                <Segmented
                    options={viewModeOptions}
                    value={viewMode}
                    onChange={(value) => setViewMode(value as ViewMode)}
                />
                <Divider type="vertical" style={{ height: 32 }} />
                <Segmented
                    options={typeFilterOptions}
                    value={typeFilter}
                    onChange={(value) => setTypeFilter(value as TypeFilter)}
                />
                <Input
                    placeholder={t('Search requests...')}
                    prefix={<SearchOutlined />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{ maxWidth: 300, marginLeft: 'auto' }}
                    allowClear
                />
            </Flex>

            {/* Views */}
            <PendingAccessRequestsView
                pendingRequests={pendingRequests}
                typeFilter={typeFilter}
                searchTerm={searchTerm}
            />
        </div>
    );
}
