import { Col, List, Typography } from 'antd';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { useNavigate } from 'react-router-dom';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { useTranslation } from 'react-i18next';
import { ReactNode } from 'react';
import { formatDate } from '@/utils/date.helper.ts';

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
};

export const PendingRequestsList = ({ isFetching, pendingActionItems }: DataProductListProps) => {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const handleItemClick = (navigatePath: string) => {
        navigate(navigatePath);
    };

    return (
        <List
            dataSource={pendingActionItems}
            loading={isFetching}
            size="small"
            locale={{ emptyText: t('There are currently no pending requests.') }}
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
                                        iconComponent={getDataProductTypeIcon('exploration')}
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
