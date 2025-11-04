import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button, Flex, List, Typography } from 'antd';
import type { PaginationConfig } from 'antd/es/pagination';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import type { ActionResolveRequest, PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { formatDate } from '@/utils/date.helper.ts';

export type PendingActionItem = {
    key: string;
    description: ReactNode;
    navigatePath: string;
    date: string;
    author: string;
    initials: string;
    message: ReactNode;
    color: string;
    tag: ReactNode;
    type: PendingActionTypes;
    request: ActionResolveRequest;
    icon: ReactNode;
    handleAccept: () => void;
    handleDeny: () => void;
};

type PendingRequestsListProps = {
    pendingActionItems: PendingActionItem[];
    pagination: PaginationConfig;
};

export const PendingRequestsList = ({ pendingActionItems, pagination }: PendingRequestsListProps) => {
    const { t } = useTranslation();

    const navigate = useNavigate();

    if (!pendingActionItems || pendingActionItems.length === 0) {
        return <EmptyList description={t('No requests available.')} />;
    }

    return (
        <List
            dataSource={pendingActionItems}
            pagination={{
                ...pagination,
                className: styles.antListPagination,
            }}
            itemLayout="vertical"
            size="large"
            split={false}
            renderItem={(item) => {
                const formattedDate = item.date ? formatDate(item.date) : '';
                return (
                    <List.Item
                        className={styles.listItem}
                        key={item.key}
                        onClick={() => navigate(item.navigatePath)}
                        actions={[
                            <Button
                                key={'accept'}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    posthog.capture(PosthogEvents.REQUESTS_ACCEPT);
                                    item.handleAccept();
                                }}
                                type="link"
                                size={'small'}
                            >
                                {t('Accept')}
                            </Button>,
                            <Button
                                key={'reject'}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    posthog.capture(PosthogEvents.REQUESTS_REJECT);
                                    item.handleDeny();
                                }}
                                type="link"
                                size={'small'}
                            >
                                {t('Reject')}
                            </Button>,
                        ]}
                        extra={
                            <Flex gap="small">
                                <Typography.Text type="secondary">{item.icon}</Typography.Text>
                                <Typography.Text>{item.tag}</Typography.Text>
                            </Flex>
                        }
                    >
                        <List.Item.Meta
                            avatar={
                                <Avatar style={{ backgroundColor: item.color }}>
                                    {item.initials || <UserOutlined />}
                                </Avatar>
                            }
                            title={item.description}
                            description={
                                <>
                                    {t('by')} {item.author}, {formattedDate}
                                </>
                            }
                        />
                        {item.message}
                    </List.Item>
                );
            }}
        />
    );
};
