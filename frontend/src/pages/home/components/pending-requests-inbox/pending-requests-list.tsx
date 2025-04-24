import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button, Flex, List, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { ActionResolveRequest } from '@/types/notifications/notification.contract';
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
    origin: ReactNode;
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
                            <List.Item.Meta
                                className={styles.itemCard}
                                avatar={
                                    <Avatar
                                        style={{ backgroundColor: item.color }}
                                        size="large"
                                        className={styles.avatar}
                                    >
                                        {item.initials || <UserOutlined />}
                                    </Avatar>
                                }
                                title={
                                    <Flex vertical gap={2}>
                                        <Typography.Text>{item.description}</Typography.Text>
                                        <Typography.Text type="secondary" style={{ fontWeight: 'normal' }}>
                                            by {item.author}, {formattedDate}
                                        </Typography.Text>
                                    </Flex>
                                }
                                description={<Typography.Text>{item.message}</Typography.Text>}
                            />
                            <Flex align="end" className={styles.actionsTopRight}>
                                <Flex className={styles.typeIndicator} gap="small">
                                    <Typography.Text className={styles.tag} type="secondary">
                                        {item.icon}
                                    </Typography.Text>
                                    <Typography.Text>{item.origin}</Typography.Text>
                                </Flex>

                                <div className={styles.buttons}>
                                    <Button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onAccept(item.request);
                                        }}
                                        className={styles.button}
                                        type="link"
                                    >
                                        {t('Accept')}
                                    </Button>
                                    <Button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onReject(item.request);
                                        }}
                                        className={styles.button}
                                        type="link"
                                    >
                                        {t('Reject')}
                                    </Button>
                                </div>
                            </Flex>
                        </List.Item>
                        <div />
                    </>
                );
            }}
        />
    );
};
