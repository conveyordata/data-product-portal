import { DeleteOutlined, ExportOutlined, NotificationOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Card, Flex, Popconfirm, Typography } from 'antd';
import { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { AnnouncementTypeTag } from '@/components/announcements/announcement-type-tag.tsx';
import { EmptyState, emptyStateQueryProps, isAwaitingData } from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { TabKeys } from '@/pages/output-port/components/dataset-tabs/dataset-tabkeys';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type Announcement,
    useGetOutputPortAnnouncementsQuery,
    useRemoveOutputPortAnnouncementMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    InputPortStatus,
    useGetInputPortsForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { formatDateFromISOString } from '@/utils/date.helper.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { NewAnnouncementModal } from './new-announcement-modal.tsx';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function AnnouncementsTab({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const announcementsQuery = useGetOutputPortAnnouncementsQuery({ id: outputPortId, dataProductId });
    const { data: { announcements = [] } = {} } = announcementsQuery;
    const { data: { allowed: canPost = false } = {} } = useCheckAccessQuery({
        resource: outputPortId,
        action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
    });
    const { data: { input_ports: inputPorts = [] } = {} } = useGetInputPortsForOutputPortQuery(
        { outputPortId, dataProductId },
        { skip: !canPost },
    );
    const consumerCount = inputPorts.filter(({ status }) => status === InputPortStatus.Approved).length;

    if (isAwaitingData(announcementsQuery)) {
        return <LoadingSpinner />;
    }

    const newAnnouncementButton = canPost && (
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            {t('New Announcement')}
        </Button>
    );

    return (
        <Flex vertical gap="middle">
            {announcements.length > 0 && newAnnouncementButton && (
                <Flex justify="flex-end">{newAnnouncementButton}</Flex>
            )}
            {announcements.length === 0 ? (
                <EmptyState
                    icon={<NotificationOutlined />}
                    title={t('No announcements yet')}
                    description={
                        canPost ? (
                            <Trans
                                t={t}
                                i18nKey="AnnouncementsEmptyProducer"
                                count={consumerCount}
                                defaults="Post one to tell every Consuming Data Product about an issue, a change they need to make, planned maintenance or a new version. <link>{{count}} Data Products</link> consume this Output Port today."
                                components={{ link: <Link to={{ search: `?tab=${TabKeys.Consumers}` }} /> }}
                            />
                        ) : (
                            t(
                                "The team that owns this Output Port hasn't posted any updates. When they do, Consuming Data Products get a notification.",
                            )
                        )
                    }
                    action={newAnnouncementButton}
                    {...emptyStateQueryProps(announcementsQuery)}
                />
            ) : (
                announcements.map((announcement) => (
                    <AnnouncementCard
                        key={announcement.id}
                        announcement={announcement}
                        canDelete={canPost}
                        dataProductId={dataProductId}
                    />
                ))
            )}
            {isModalOpen && (
                <NewAnnouncementModal
                    dataProductId={dataProductId}
                    outputPortId={outputPortId}
                    consumerCount={consumerCount}
                    onClose={() => setIsModalOpen(false)}
                />
            )}
        </Flex>
    );
}

type CardProps = {
    announcement: Announcement;
    canDelete: boolean;
    dataProductId: string;
};

function AnnouncementCard({ announcement, canDelete, dataProductId }: CardProps) {
    const { t } = useTranslation();
    const [removeAnnouncement, { isLoading }] = useRemoveOutputPortAnnouncementMutation();
    const author = announcement.author
        ? `${announcement.author.first_name} ${announcement.author.last_name}`
        : t('a former user');

    const onDelete = async () => {
        try {
            await removeAnnouncement({
                dataProductId,
                id: announcement.output_port_id,
                announcementId: announcement.id,
            }).unwrap();
            dispatchMessage({ content: t('Announcement deleted'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Could not delete announcement'), type: 'error' });
        }
    };

    return (
        <Card size="small">
            <Flex justify="space-between" align="center" gap="middle">
                <Flex vertical gap="small">
                    <Flex align="center" gap="small" wrap>
                        <AnnouncementTypeTag type={announcement.type} />
                        <Typography.Text strong>{announcement.title}</Typography.Text>
                    </Flex>
                    <Typography.Paragraph style={{ whiteSpace: 'pre-line', marginBottom: 0 }}>
                        {announcement.message}
                    </Typography.Paragraph>
                    <Typography.Text type="secondary">
                        {t('Posted {{date}} by {{author}}', {
                            date: formatDateFromISOString(announcement.created_at),
                            author,
                        })}
                    </Typography.Text>
                </Flex>
                <Flex gap="small" align="center">
                    {announcement.link && (
                        <Button
                            size="small"
                            href={announcement.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            icon={<ExportOutlined />}
                            iconPlacement="end"
                        >
                            {t('Read more')}
                        </Button>
                    )}
                    {canDelete && (
                        <Popconfirm
                            title={t('Delete Announcement')}
                            description={t(
                                'Consumers will no longer see it. The deletion is recorded in History. This cannot be undone.',
                            )}
                            okText={t('Delete')}
                            okButtonProps={{ danger: true, loading: isLoading }}
                            cancelText={t('Cancel')}
                            onConfirm={onDelete}
                        >
                            <Button size="small" type="link" danger icon={<DeleteOutlined />}>
                                {t('Delete')}
                            </Button>
                        </Popconfirm>
                    )}
                </Flex>
            </Flex>
        </Card>
    );
}
