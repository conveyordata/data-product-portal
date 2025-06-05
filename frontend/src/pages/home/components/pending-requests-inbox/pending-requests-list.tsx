import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button, Flex, List, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import type { ActionResolveRequest } from '@/types/pending-actions/pending-actions';
import { formatDate } from '@/utils/date.helper.ts';
import type { PaginationConfig } from 'antd/es/pagination';

type PendingActionItem = {
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
            className={styles.antList}
            pagination={{
                ...pagination,
                className: styles.antListPagination,
            }}
            renderItem={(item) => {
                const formattedDate = item.date ? formatDate(item.date) : '';
                return (
                    <>
                        <List.Item
                            key={item.key}
                            className={styles.listItem}
                            onClick={() => handleItemClick(item.navigatePath)}
                        >
                            <Flex vertical className={styles.itemCard} gap={8}>
                                <Flex align="center">
                                    <Avatar
                                        style={{ backgroundColor: item.color }}
                                        className={styles.avatar}
                                        size="large"
                                    >
                                        {item.initials || <UserOutlined />}
                                    </Avatar>
                                    <Flex vertical className={styles.width}>
                                        <Flex justify="space-between">
                                            <Typography.Text>{item.description}</Typography.Text>
                                            <Flex>
                                                <Flex gap="small">
                                                    <Typography.Text type="secondary">{item.icon}</Typography.Text>
                                                    <Typography.Text>{item.tag}</Typography.Text>
                                                </Flex>

                                                <Flex align="center" justify="space-evenly" className={styles.buttons}>
                                                    <Button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onAccept(item.request);
                                                        }}
                                                        type="link"
                                                        className={styles.resolveButton}
                                                    >
                                                        {t('Accept')}
                                                    </Button>
                                                    <Button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onReject(item.request);
                                                        }}
                                                        type="link"
                                                        className={styles.resolveButton}
                                                    >
                                                        {t('Reject')}
                                                    </Button>
                                                </Flex>
                                            </Flex>
                                        </Flex>
                                        <Typography.Text type="secondary">
                                            by {item.author}, {formattedDate}
                                        </Typography.Text>
                                    </Flex>
                                </Flex>
                                <Typography.Text className={styles.message}>{item.message}</Typography.Text>
                            </Flex>
                        </List.Item>
                        <div />
                    </>
                );
            }}
        />
    );
};
