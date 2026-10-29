import { CheckOutlined } from '@ant-design/icons';
import { Button, Flex, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { AnnouncementTypeIcon, AnnouncementTypeLabel } from '@/components/announcements/announcement-type.tsx';
import { TabKeys as DatasetTabKeys } from '@/pages/output-port/components/dataset-tabs/dataset-tabkeys.ts';
import type { GetUserNotificationsResponseItem } from '@/store/api/services/generated/usersNotificationsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { formatDateFromISOString, formatDateToNowFromUTCString } from '@/utils/date.helper';
import { linkify } from '@/utils/linkify.tsx';

type Props = {
    notification: GetUserNotificationsResponseItem;
    onAcknowledge: (id: string) => void;
    isAcknowledging?: boolean;
    detailed?: boolean;
};

export function AnnouncementNotification({
    notification,
    onAcknowledge,
    isAcknowledging = false,
    detailed = false,
}: Props) {
    const { t } = useTranslation();
    const { announcement, output_port, created_on } = notification.event;
    if (!announcement || !output_port) return null;

    const outputPortPath = createMarketplaceOutputPortPath(
        output_port.id,
        output_port.data_product_id,
        DatasetTabKeys.Announcements,
    );

    const details = (
        <Flex vertical gap="small" style={{ maxWidth: '25em' }}>
            <AnnouncementTypeLabel type={announcement.type} />
            <Typography.Paragraph style={{ whiteSpace: 'pre-line', marginBottom: 0 }}>
                {linkify(announcement.message)}
            </Typography.Paragraph>
            <Typography.Text type="secondary">
                {t('Posted {{date}} on', { date: formatDateFromISOString(announcement.created_at) })}{' '}
                <Link to={outputPortPath}>{output_port.name}</Link>
            </Typography.Text>
        </Flex>
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
                <Flex align="center" gap="small">
                    <Typography.Text type="secondary" ellipsis>
                        {output_port.name} · {formatDateToNowFromUTCString(created_on)}
                    </Typography.Text>
                    {detailed && (
                        <Popover content={details} title={announcement.title} trigger="click" placement="bottomLeft">
                            <Button type="link" size="small" style={{ padding: 0, height: 'auto' }}>
                                {t('Read more')}
                            </Button>
                        </Popover>
                    )}
                </Flex>
            </Flex>
            <Button
                type={detailed ? 'default' : 'text'}
                size={detailed ? 'small' : 'middle'}
                aria-label={t('Acknowledge')}
                icon={<CheckOutlined />}
                loading={isAcknowledging}
                disabled={isAcknowledging}
                onClick={(e) => {
                    e.stopPropagation();
                    onAcknowledge(notification.id);
                }}
            >
                {detailed && t('Acknowledge')}
            </Button>
        </Flex>
    );
}
