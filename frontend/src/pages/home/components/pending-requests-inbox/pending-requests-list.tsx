import { Col, List, Typography } from 'antd';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { useNavigate } from 'react-router-dom';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { useTranslation } from 'react-i18next';
import { ReactNode } from 'react';
import { formatDate } from '@/utils/date.helper.ts';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import { PaginationConfig } from 'antd/es/pagination';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';

const COL_SPAN = 12;

type PendingActionItem = {
    key: string;
    description: ReactNode;
    navigatePath: string;
    date: string | undefined;
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
                        <List.Item
                            key={item.key}
                            className={styles.listItem}
                            onClick={() => handleItemClick(item.navigatePath)}
                        >
                            <List.Item.Meta
                                className={styles.itemCard}
                                avatar={
                                    <CustomSvgIconLoader
                                        iconComponent={getDataProductTypeIcon()}
                                        hasRoundBorder
                                        size={'default'}
                                    />
                                }
                                description={item.description}
                            />

                            <Col span={COL_SPAN} className={styles.actionContainer}>
                                {formattedDate && (
                                    <div className={styles.dateSection}>
                                        <Typography.Text type="secondary">{t('Received on')}</Typography.Text>
                                        <Typography.Text>{t('{{date}}', { date: formattedDate })}</Typography.Text>
                                    </div>
                                )}
                            </Col>
                        </List.Item>
                        <div />
                    </>
                );
            }}
        />
    );
};
