import { List } from 'antd';
import type { PaginationConfig } from 'antd/es/pagination';
import { useTranslation } from 'react-i18next';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import type { PendingAction } from '@/types/pending-actions/pending-actions';
import { PendingItem } from './pending-request-item';

type PendingRequestsListProps = {
    pendingActions: PendingAction[];
    pagination: PaginationConfig;
};

export const PendingRequestsList = ({ pendingActions, pagination }: PendingRequestsListProps) => {
    const { t } = useTranslation();

    if (!pendingActions || pendingActions.length === 0) {
        return <EmptyList description={t('No requests available.')} />;
    }

    return (
        <List
            dataSource={pendingActions}
            pagination={{
                ...pagination,
                className: styles.antListPagination,
            }}
            itemLayout="vertical"
            size="large"
            split={false}
            renderItem={(item) => <PendingItem pendingAction={item} />}
        />
    );
};
