import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button, Flex, List, Typography } from 'antd';
import type { PaginationConfig } from 'antd/es/pagination';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
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
    request: ActionResolveRequest;
    icon: ReactNode;
    type: PendingActionTypes;
};

type PendingRequestsListProps = {
    pendingActionItems: PendingActionItem[];
    pagination: PaginationConfig;
    onAccept: (request: ActionResolveRequest) => void;
    onReject: (request: ActionResolveRequest) => void;
};
export const PendingRequestsList = ({
    pendingActionItems,
    pagination,
    onAccept,
    onReject,
}: PendingRequestsListProps) => {
    const { t } = useTranslation();

    const navigate = useNavigate();

    if (!pendingActionItems || pendingActionItems.length === 0) {
        return <EmptyList description={t('No requests available.')} />;
    }

    const handleItemClick = (navigatePath: string) => {
        navigate(navigatePath);
    };

    return (
        <List
            dataSource={pendingActionItems}
            pagination={{
                ...pagination,
                className: styles.antListPagination,
            }}
            split={false}
            renderItem={(item) => {
                const formattedDate = item.date ? formatDate(item.date) : '';
                return (
                    <List.Item
                        key={item.key}
                        className={styles.listItem}
                        onClick={() => handleItemClick(item.navigatePath)}
                        actions={[
                            <Button
                                key={'accept'}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onAccept(item.request);
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
                                    onReject(item.request);
                                }}
                                type="link"
                                size={'small'}
                            >
                                {t('Reject')}
                            </Button>,
                        ]}
                    >
                        <Flex vertical className={styles.itemCard} gap={'small'}>
                            <Flex align="center">
                                <Avatar style={{ backgroundColor: item.color }} className={styles.avatar} size="large">
                                    {item.initials || <UserOutlined />}
                                </Avatar>
                                <Flex vertical flex={1}>
                                    <Flex justify="space-between">
                                        <Typography.Text>{item.description}</Typography.Text>
                                        <Flex>
                                            <Flex gap="small">
                                                <Typography.Text type="secondary">{item.icon}</Typography.Text>
                                                <Typography.Text>{item.tag}</Typography.Text>
                                            </Flex>
                                        </Flex>
                                    </Flex>
                                    <Typography.Text type="secondary">
                                        by {item.author}, {formattedDate}
                                    </Typography.Text>
                                </Flex>
                            </Flex>
                            <Typography.Text>{item.message}</Typography.Text>
                        </Flex>
                    </List.Item>
                );
            }}
        />
    );
};
