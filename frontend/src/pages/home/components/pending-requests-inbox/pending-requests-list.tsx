import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button, Flex, List, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { ActionResolveRequest } from '@/types/pending-actions/pending-actions';
import { ListPaginationConfig } from '@/types/shared/lists';
import { formatDate } from '@/utils/date.helper.ts';

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

type DataProductListProps = {
    pendingActionItems: PendingActionItem[];
    pagination: ListPaginationConfig;
    onAccept: (request: ActionResolveRequest) => void;
    onReject: (request: ActionResolveRequest) => void;
};

export const PendingRequestsList = ({ pendingActionItems, pagination, onAccept, onReject }: DataProductListProps) => {
    const { t } = useTranslation();

    const navigate = useNavigate();

    if (!pendingActionItems || pendingActionItems.length === 0) {
        return <EmptyList description={t(`No requests available.`)} />;
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
                            <Flex vertical className={styles.itemCard} gap={4}>
                                <Flex align="center">
                                    <Avatar
                                        style={{ backgroundColor: item.color }}
                                        className={styles.avatar}
                                        size="large"
                                    >
                                        {item.initials || <UserOutlined />}
                                    </Avatar>
                                    <Flex vertical>
                                        <Typography.Text>{item.description}</Typography.Text>
                                        <Typography.Text type="secondary" style={{ fontWeight: 'normal' }}>
                                            by {item.author}, {formattedDate}
                                        </Typography.Text>
                                    </Flex>
                                    <Flex align="flex-start" justify="flex-start" className={styles.endActions}>
                                        <Flex className={styles.typeIndicator} gap="small">
                                            <Typography.Text type="secondary">{item.icon}</Typography.Text>
                                            <Typography.Text>{item.tag}</Typography.Text>
                                        </Flex>

                                        <Button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onAccept(item.request);
                                            }}
                                            type="link"
                                        >
                                            {t('Accept')}
                                        </Button>
                                        <Button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onReject(item.request);
                                            }}
                                            type="link"
                                        >
                                            {t('Reject')}
                                        </Button>
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
