import { Divider, Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import styles from './history-event-badge.module.scss';

type Props = {
    name: string;
    author: string;
    date: Date;
};

// Todo: Expand on this badge component to show more information about the event when the event structure is known
// This component is made to be used in the History tab
export function HistoryEventBadge({ name, author, date }: Props) {
    const { t } = useTranslation();
    return (
        <Flex vertical className={styles.badgeContainer}>
            <Divider style={{ margin: 0 }} />
            <Flex vertical>
                <Typography.Text strong>{name}</Typography.Text>
                <Typography.Text type="secondary">
                    {t('by {{author}} on {{date}}', {
                        author,
                        date: date.toLocaleDateString(),
                    })}
                </Typography.Text>
            </Flex>
            <Divider style={{ margin: 0 }} />
        </Flex>
    );
}
