import { CheckOutlined } from '@ant-design/icons';
import { Button, Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { AnnouncementTypeIcon } from '@/components/announcements/announcement-type.tsx';
import { TabKeys as DatasetTabKeys } from '@/pages/output-port/components/dataset-tabs/dataset-tabkeys.ts';
import type { GetUserNotificationsResponseItem } from '@/store/api/services/generated/usersNotificationsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { formatDateToNowFromUTCString } from '@/utils/date.helper';

type Props = {
    notification: GetUserNotificationsResponseItem;
    onAcknowledge: (id: string) => void;
    isAcknowledging?: boolean;
    disabled?: boolean;
};

export function AnnouncementNotification({
    notification,
    onAcknowledge,
    isAcknowledging = false,
    disabled = false,
}: Props) {
    const { t } = useTranslation();
    const { announcement, output_port, created_on } = notification.event;
    if (!announcement || !output_port) return null;

    const outputPortPath = createMarketplaceOutputPortPath(
        output_port.id,
        output_port.data_product_id,
        DatasetTabKeys.Announcements,
    );

    return (
        <Flex justify="space-between" align="center" gap="small">
            <Flex vertical flex={1} style={{ minWidth: 0 }}>
                <Link to={outputPortPath}>
                    <Flex align="center" gap="small">
                        <AnnouncementTypeIcon type={announcement.type} />
                        <Typography.Text strong ellipsis={{ tooltip: announcement.title }}>
                            {announcement.title}
                        </Typography.Text>
                    </Flex>
                </Link>
                <Typography.Text type="secondary" ellipsis>
                    {output_port.name} · {formatDateToNowFromUTCString(created_on)}
                </Typography.Text>
            </Flex>
            <Button
                type="text"
                aria-label={t('Acknowledge')}
                icon={<CheckOutlined />}
                loading={isAcknowledging}
                disabled={isAcknowledging || disabled}
                onClick={(e) => {
                    e.stopPropagation();
                    onAcknowledge(notification.id);
                }}
            />
        </Flex>
    );
}
