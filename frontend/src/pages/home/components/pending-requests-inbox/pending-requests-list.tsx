import { DownOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Dropdown, List, Menu, Space, Typography } from 'antd';
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
};

type DataProductListProps = {
    isFetching: boolean;
    pendingActionItems: PendingActionItem[];
};

export const PendingRequestsList = ({ isFetching, pendingActionItems }: DataProductListProps) => {
    const navigate = useNavigate();

    if (isFetching) return <LoadingSpinner />;

    if (!pendingActionItems || pendingActionItems.length === 0) {
        return;
    }

    const handleItemClick = (navigatePath: string) => {
        navigate(navigatePath);
    };

    return (
        <List
            dataSource={pendingActionItems}
            className={styles.antList}
            renderItem={(item) => {
                const formattedDate = item.date ? formatDate(item.date) : undefined;
                return (
                    <>
                        <Space size={0} className={styles.listItemTopInfo}>
                            <Space align="center">
                                <UserOutlined />
                                <Typography.Text>{item.author}</Typography.Text>
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
                                        className={styles.actionOptions}
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
