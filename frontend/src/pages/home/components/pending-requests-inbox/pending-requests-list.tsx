import { ArrowRightOutlined, DownOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Dropdown, List, Menu, Space, Typography } from 'antd';
import type { PaginationConfig } from 'antd/es/pagination';
import type { ReactNode } from 'react';
import { useNavigate } from 'react-router';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { formatDate } from '@/utils/date.helper.ts';

type PendingActionItem = {
    key: string;
    description: ReactNode;
    navigatePath: string;
    date: string;
    author: string;
    origin: ReactNode;
};

type DataProductListProps = {
    isFetching: boolean;
    pendingActionItems: PendingActionItem[];
    pagination: PaginationConfig;
    isFirstHalf: boolean;
};

export const PendingRequestsList = ({
    isFetching,
    pendingActionItems,
    pagination,
    isFirstHalf,
}: DataProductListProps) => {
    const navigate = useNavigate();

    if (isFetching || !(pagination.current && pagination.pageSize)) return <LoadingSpinner />;

    if (!pendingActionItems || pendingActionItems.length === 0) {
        return;
    }

    const handleItemClick = (navigatePath: string) => {
        navigate(navigatePath);
    };

    const totalItems = pagination.pageSize;
    const half = Math.ceil(totalItems / 2);
    const itemsToRender = isFirstHalf
        ? pendingActionItems.slice(0, half)
        : pendingActionItems.slice(half, pagination.pageSize);
    const currentPage = pagination.current - 1;
    const pageSize = pagination.pageSize;
    const startIndex = currentPage * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedItems = itemsToRender.slice(startIndex, endIndex);

    if (paginatedItems.length == 0 && isFirstHalf == false) return;

    return (
        <List
            dataSource={paginatedItems}
            className={styles.antList}
            renderItem={(item) => {
                const formattedDate = item.date ? formatDate(item.date) : undefined;
                return (
                    <>
                        <Space size={0} className={styles.listItemTopInfo}>
                            <Space align="center">
                                <UserOutlined />
                                <Typography.Text>{item.author}</Typography.Text>
                                {item.origin && (
                                    <Typography.Text>
                                        <ArrowRightOutlined /> {item.origin}
                                    </Typography.Text>
                                )}
                            </Space>
                            <Space>
                                <Typography.Text type="secondary">{formattedDate}</Typography.Text>
                            </Space>
                        </Space>
                        <List.Item
                            key={item.key}
                            className={styles.listItem}
                            onClick={() => handleItemClick(item.navigatePath)}
                        >
                            <List.Item.Meta className={styles.itemCard} description={item.description} />
                            <div>
                                <Dropdown
                                    trigger={['click']}
                                    placement="bottomRight"
                                    dropdownRender={() => (
                                        <Menu>
                                            <Menu.Item key="accept">Accept</Menu.Item>
                                            <Menu.Item key="deny">Deny</Menu.Item>
                                        </Menu>
                                    )}
                                >
                                    <Button
                                        icon={<DownOutlined />}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                        }}
                                    ></Button>
                                </Dropdown>
                            </div>
                        </List.Item>

                        <div />
                    </>
                );
            }}
        />
    );
};
