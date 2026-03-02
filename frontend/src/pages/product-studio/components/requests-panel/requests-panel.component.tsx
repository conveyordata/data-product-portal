import { Flex, Input } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi';
import { PendingAccessRequestsView } from './pending-access-requests-view';

export function RequestsPanel() {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState('');

    const { data: { pending_actions: pendingRequests = [] } = {} } = useGetUserPendingActionsQuery();

    // Get counts for badges

    return (
        <Flex vertical gap="small">
            {/* Toolbar with segmented controls and search */}
            <Input.Search
                placeholder={t('Search requests...')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ maxWidth: 400 }}
                allowClear
            />

            {/* Views */}
            <PendingAccessRequestsView pendingRequests={pendingRequests} searchTerm={searchTerm} />
        </Flex>
    );
}
