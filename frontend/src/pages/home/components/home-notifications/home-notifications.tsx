import { ArrowRightOutlined, WarningOutlined } from '@ant-design/icons';
import { Button, Card, Col, Divider, Flex, Row, Space, Typography, theme } from 'antd';
import { type ReactNode, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { ANNOUNCEMENT_URGENCY } from '@/components/announcements/announcement-type.tsx';
import { EmptyState, hasFailed } from '@/components/empty-state/empty-state.component.tsx';
import { AnnouncementNotification } from '@/components/notifications/announcement-notification.tsx';
import {
    isAnnouncementNotification,
    useAcknowledgeNotification,
} from '@/components/notifications/use-acknowledge-notification.ts';
import { acceptRequest, rejectRequest } from '@/components/pending-access-requests-modal/request-handlers.ts';
import { ReviewButton } from '@/components/pending-access-requests-modal/review-button.tsx';
import { ReviewRequestModal } from '@/components/pending-access-requests-modal/review-request-modal.tsx';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { transformToTableRow } from '@/pages/product-studio/components/requests/request-utils.ts';
import { TabKeys } from '@/pages/product-studio/product-studio-tabkeys.ts';
import { AnnouncementType } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import {
    useGetUserNotificationsQuery,
    useRemoveUserNotificationMutation,
} from '@/store/api/services/generated/usersNotificationsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import type { Request } from '@/types/request-types/request-types.tsx';
import { formatDate } from '@/utils/date.helper.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

const MAX_BODY_HEIGHT = 400;

function Section({ title, extra, items }: { title: string; extra?: ReactNode; items: ReactNode[] }) {
    const { token } = theme.useToken();
    return (
        <Col xs={24} lg={12}>
            <Card
                size="small"
                title={title}
                extra={extra}
                style={{ borderColor: token.colorPrimaryBorder, height: '100%' }}
                styles={{
                    header: {
                        backgroundColor: token.colorPrimaryBg,
                        borderColor: token.colorPrimaryBorder,
                        color: token.colorPrimaryText,
                    },
                    body: { maxHeight: MAX_BODY_HEIGHT, overflowY: 'auto' },
                }}
            >
                <Space
                    orientation="vertical"
                    separator={<Divider size="small" />}
                    style={{ width: '100%' }}
                    styles={{ item: { width: '100%' } }}
                >
                    {items}
                </Space>
            </Card>
        </Col>
    );
}

export function HomeNotifications() {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const pendingActionsQuery = useGetUserPendingActionsQuery();
    const notificationsQuery = useGetUserNotificationsQuery();
    const { acknowledge, acknowledgingId } = useAcknowledgeNotification();
    const [removeNotification, { isLoading: isAcknowledgingAll }] = useRemoveUserNotificationMutation();
    const handlers = usePendingActionHandlers();
    const [reviewingAction, setReviewingAction] = useState<Request | null>(null);

    const pendingActions = pendingActionsQuery.data?.pending_actions;
    const notifications = notificationsQuery.data?.notifications;

    const requestRows = useMemo(
        () =>
            (pendingActions ?? [])
                .map(transformToTableRow)
                .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()),
        [pendingActions],
    );

    const announcements = useMemo(
        () =>
            (notifications ?? [])
                .filter((n) => isAnnouncementNotification(n) && n.event.announcement && n.event.output_port)
                .sort((a, b) => {
                    const urgency =
                        ANNOUNCEMENT_URGENCY.indexOf(a.event.announcement?.type ?? AnnouncementType.Info) -
                        ANNOUNCEMENT_URGENCY.indexOf(b.event.announcement?.type ?? AnnouncementType.Info);
                    return urgency || new Date(b.event.created_on).getTime() - new Date(a.event.created_on).getTime();
                }),
        [notifications],
    );

    const acknowledgeAllAnnouncements = async () => {
        try {
            await Promise.all(announcements.map(({ id }) => removeNotification(id).unwrap()));
            dispatchMessage({ content: t('Announcements have been acknowledged'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to acknowledge announcements'), type: 'error' });
        }
    };

    const isEmpty = requestRows.length === 0 && announcements.length === 0;
    const failed = isEmpty && (hasFailed(pendingActionsQuery) || hasFailed(notificationsQuery));
    if (isEmpty && !failed && reviewingAction === null) return null;

    return (
        <Flex vertical gap="middle" style={{ marginBottom: 48 }}>
            {failed ? (
                <EmptyState
                    size="small"
                    icon={<WarningOutlined />}
                    title={t("Couldn't load this section")}
                    error
                    onRetry={() => {
                        pendingActionsQuery.refetch();
                        notificationsQuery.refetch();
                    }}
                />
            ) : (
                <Row gutter={[24, 24]}>
                    {requestRows.length > 0 && (
                        <Section
                            title={t('Waiting for your decision ({{count}})', { count: requestRows.length })}
                            extra={
                                <Link
                                    to={{
                                        pathname: ApplicationPaths.Studio,
                                        search: `?tab=${TabKeys.PendingRequests}`,
                                    }}
                                >
                                    {t('View all')} <ArrowRightOutlined />
                                </Link>
                            }
                            items={requestRows.map((row) => (
                                <Flex key={row.key} align="center" gap="small">
                                    <UserAvatar
                                        user={row.requestedBy ?? undefined}
                                        color={token.colorPrimary}
                                        size="small"
                                    />
                                    <Flex vertical flex={1} style={{ minWidth: 0 }}>
                                        <Typography.Text ellipsis={{ tooltip: row.description }}>
                                            {row.description}
                                        </Typography.Text>
                                        <Typography.Text type="secondary">{formatDate(row.date)}</Typography.Text>
                                    </Flex>
                                    <ReviewButton action={row.pendingAction} onReview={setReviewingAction} />
                                </Flex>
                            ))}
                        />
                    )}
                    {announcements.length > 0 && (
                        <Section
                            title={t('Announcements ({{count}})', { count: announcements.length })}
                            extra={
                                <Button
                                    type="link"
                                    size="small"
                                    loading={isAcknowledgingAll}
                                    onClick={acknowledgeAllAnnouncements}
                                >
                                    {t('Acknowledge all')}
                                </Button>
                            }
                            items={announcements.map((notification) => (
                                <AnnouncementNotification
                                    key={notification.id}
                                    notification={notification}
                                    onAcknowledge={acknowledge}
                                    isAcknowledging={acknowledgingId === notification.id}
                                    detailed
                                />
                            ))}
                        />
                    )}
                </Row>
            )}
            <ReviewRequestModal
                action={reviewingAction}
                open={reviewingAction !== null}
                onClose={() => setReviewingAction(null)}
                onAccept={(action, decisionNote) => acceptRequest(action, handlers, decisionNote)}
                onReject={(action, decisionNote) => rejectRequest(action, handlers, decisionNote)}
            />
        </Flex>
    );
}
