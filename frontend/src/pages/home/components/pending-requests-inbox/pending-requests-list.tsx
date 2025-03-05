import { UserOutlined } from '@ant-design/icons';
import { List, Space, Typography } from 'antd';
import type { PaginationConfig } from 'antd/es/pagination';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { formatDate } from '@/utils/date.helper.ts';

type PendingActionItem = {
    key: string;
    description: ReactNode;
    navigatePath: string;
    date: string;
    author: string;
} | null;

type DataProductListProps = {
    isFetching: boolean;
    pendingActionItems: PendingActionItem[];
    pagination: PaginationConfig;
};

export const PendingRequestsList = ({ isFetching, pendingActionItems, pagination }: DataProductListProps) => {
    const { t } = useTranslation();
    const navigate = useNavigate();

    if (isFetching) return <LoadingSpinner />;

    if (!pendingActionItems || pendingActionItems.length === 0) {
        return <EmptyList description={t(`There are currently no pending requests.`)} />;
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
                if (!item) return null;
                const formattedDate = item.date ? formatDate(item.date) : undefined;
                return (
                    <>
                        <Space size={0} className={styles.listItemTopInfo}>
                            <Space align="center">
                                <UserOutlined />
                                <Typography.Text>{t('{{name}}', { name: item.author })}</Typography.Text>
                            </Space>
                            <Space>
                                <Typography.Text type="secondary">
                                    {t('{{date}}', { date: formattedDate })}
                                </Typography.Text>
                            </Space>
                        </Space>

                        <List.Item
                            key={item.key}
                            className={styles.listItem}
                            onClick={() => handleItemClick(item.navigatePath)}
                        >
                            <List.Item.Meta className={styles.itemCard} description={item.description} />
                        </List.Item>
                        <div />
                    </>
                );
            }}
        />
    );
};
