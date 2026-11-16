import { NotificationOutlined } from '@ant-design/icons';
import { Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { isAnnouncementNotification } from '@/components/notifications/use-acknowledge-notification.ts';
import { TabKeys as DatasetTabKeys } from '@/pages/output-port/components/dataset-tabs/dataset-tabkeys.ts';
import { useGetUserNotificationsQuery } from '@/store/api/services/generated/usersNotificationsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function NewAnnouncementsTag({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: { notifications = [] } = {} } = useGetUserNotificationsQuery();
    const count = notifications.filter(
        (notification) => isAnnouncementNotification(notification) && notification.event.subject_id === outputPortId,
    ).length;

    if (count === 0) return null;

    return (
        <Link to={createMarketplaceOutputPortPath(outputPortId, dataProductId, DatasetTabKeys.Announcements)}>
            <Tag icon={<NotificationOutlined />}>{t('{{count}} new announcements', { count })}</Tag>
        </Link>
    );
}
