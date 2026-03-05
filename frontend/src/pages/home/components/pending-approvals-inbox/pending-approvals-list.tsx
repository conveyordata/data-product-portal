import { List } from 'antd';
import type { PaginationConfig } from 'antd/es/pagination';
import { useTranslation } from 'react-i18next';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import styles from '@/pages/home/components/pending-approvals-inbox/pending-approvals-inbox.module.scss';
import type { PendingAction } from '@/pages/home/components/pending-approvals-inbox/pending-approvals-inbox.tsx';
import { PendingItem } from '@/pages/home/components/pending-approvals-inbox/pending-approvals-item.tsx';

type PendingRequestsListProps = {
    pendingActions: PendingAction[];
    pagination: PaginationConfig;
};

export const PendingApprovalsList = ({ pendingActions, pagination }: PendingRequestsListProps) => {
    const { t } = useTranslation();

    if (!pendingActions || pendingActions.length === 0) {
        return <EmptyList description={t('All requests handled!')} />;
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
