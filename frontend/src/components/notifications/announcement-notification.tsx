import { CheckOutlined } from '@ant-design/icons';
import { Button, Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { AnnouncementTypeTag } from '@/components/announcements/announcement-type-tag.tsx';
import { TabKeys as DatasetTabKeys } from '@/pages/output-port/components/dataset-tabs/dataset-tabkeys.ts';
import type { GetUserNotificationsResponseItem } from '@/store/api/services/generated/usersNotificationsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { formatDateToNowFromUTCString } from '@/utils/date.helper';

type Props = {
    notification: GetUserNotificationsResponseItem;
    onAcknowledge: (id: string) => void;
    isAcknowledging?: boolean;
};

export function AnnouncementNotification({ notification, onAcknowledge, isAcknowledging = false }: Props) {
    const { t } = useTranslation();
    const { announcement, output_port, created_on } = notification.event;
    if (!announcement || !output_port) return null;

    return (
        <Flex justify="space-between" align="flex-start" gap="small">
            <Link
                to={createMarketplaceOutputPortPath(
                    output_port.id,
                    output_port.data_product_id,
                    DatasetTabKeys.Announcements,
                )}
            >
                <Flex vertical gap="small">
                    <Flex wrap align="center" gap="small">
                        <AnnouncementTypeTag type={announcement.type} />
                        <Typography.Text strong>{output_port.name}</Typography.Text>
                    </Flex>
                    <Typography.Text>{announcement.title}</Typography.Text>
                    <Typography.Text type="secondary">{formatDateToNowFromUTCString(created_on)}</Typography.Text>
                </Flex>
            </Link>
            <Button
                type="text"
                aria-label={t('Acknowledge')}
                icon={<CheckOutlined />}
                loading={isAcknowledging}
                disabled={isAcknowledging}
                onClick={(e) => {
                    e.stopPropagation();
                    onAcknowledge(notification.id);
                }}
            />
        </Flex>
    );
}
