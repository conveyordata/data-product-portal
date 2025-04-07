import { CheckOutlined, CloseOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Badge, Button, Col, Flex, List, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
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
};

type DataProductListProps = {
    isFetching: boolean;
    pendingActionItems: PendingActionItem[];
    pagination: ListPaginationConfig;
    onAccept: (request: ActionResolveRequest) => void;
    onReject: (request: ActionResolveRequest) => void;
};

const COL_SPAN = 12;

export const PendingRequestsList = ({
    isFetching,
    pendingActionItems,
    pagination,
    onAccept,
    onReject,
}: DataProductListProps) => {
    const { t } = useTranslation();

    const navigate = useNavigate();

    if (isFetching) return <LoadingSpinner />;

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
                const formattedDate = item.date ? formatDate(item.date) : undefined;
                return (
                    <>
                        <List.Item
                            key={item.key}
                            className={styles.listItem}
                            onClick={() => handleItemClick(item.navigatePath)}
                        >
                            <div className={styles.userBadge}>
                                <Badge showZero={false} color={item.color} size="default">
                                    <Avatar style={{ backgroundColor: item.color }}>
                                        {item.initials || <UserOutlined />}
                                    </Avatar>
                                </Badge>
                            </div>
                            <Flex vertical={true} className={styles.flex} align="flex-start">
                                <div className={styles.itemContainer}>
                                    <Col span={COL_SPAN}>
                                        <Flex vertical>
                                            <Typography.Text>
                                                <strong>{item.author}</strong>, {item.description}
                                            </Typography.Text>
                                            <Typography.Text type="secondary">{formattedDate}</Typography.Text>
                                        </Flex>
                                    </Col>
                                    <div className={styles.rightColumn}>
                                        <Flex justify="end">
                                            <Flex>
                                                <Typography.Text className={styles.typeIndicator} type="secondary">
                                                    {t('Originating from:')} {item.origin}
                                                </Typography.Text>{' '}
                                            </Flex>
                                            <div
                                                style={{
                                                    borderColor: item.color,
                                                    boxShadow: `0 -4px 0 0 ${item.color}`,
                                                }}
                                            >
                                                <Button
                                                    className={styles.resolveButton}
                                                    icon={<CheckOutlined />}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onAccept(item.request);
                                                    }}
                                                />
                                                <Button
                                                    className={styles.resolveButton}
                                                    icon={<CloseOutlined />}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onReject(item.request);
                                                    }}
                                                />
                                            </div>
                                        </Flex>
                                    </div>
                                </div>
                                <Typography.Text>{item.message}</Typography.Text>
                            </Flex>
                        </List.Item>

                        <div />
                    </>
                );
            }}
        />
    );
};
