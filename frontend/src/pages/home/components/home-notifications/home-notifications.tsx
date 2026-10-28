import { ArrowRightOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { Card, Col, Flex, Row, Typography, theme } from 'antd';
import { type ReactNode, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { EmptyState, hasFailed, isAwaitingData } from '@/components/empty-state/empty-state.component.tsx';
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
import { useGetUserNotificationsQuery } from '@/store/api/services/generated/usersNotificationsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import type { Request } from '@/types/request-types/request-types.tsx';
import { formatDate } from '@/utils/date.helper.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

const MAX_ITEMS = 5;
const URGENCY = [
    AnnouncementType.Issue,
    AnnouncementType.ActionNeeded,
    AnnouncementType.PlannedMaintenance,
    AnnouncementType.NewVersion,
    AnnouncementType.Info,
];

function Section({ title, extra, items }: { title: string; extra?: ReactNode; items: ReactNode[] }) {
    return (
        <Col xs={24} lg={12}>
            <Card size="small" title={title} extra={extra}>
                <Flex vertical gap="middle">
                    {items}
                </Flex>
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
                        URGENCY.indexOf(a.event.announcement?.type ?? AnnouncementType.Info) -
                        URGENCY.indexOf(b.event.announcement?.type ?? AnnouncementType.Info);
                    return urgency || new Date(b.event.created_on).getTime() - new Date(a.event.created_on).getTime();
                }),
        [notifications],
    );

    if (isAwaitingData(pendingActionsQuery) || isAwaitingData(notificationsQuery)) return null;

    const isEmpty = requestRows.length === 0 && announcements.length === 0;
    const failed = isEmpty && (hasFailed(pendingActionsQuery) || hasFailed(notificationsQuery));

    return (
        <Flex vertical gap="middle">
            <Typography.Title level={4}>{t('Notifications')}</Typography.Title>
            {isEmpty ? (
                <EmptyState
                    size="small"
                    icon={<CheckCircleOutlined />}
                    title={t("You're all caught up")}
                    description={t(
                        'No requests are waiting for your decision and there are no new Announcements on the Output Ports you consume.',
                    )}
                    error={failed}
                    onRetry={() => {
                        pendingActionsQuery.refetch();
                        notificationsQuery.refetch();
                    }}
                />
            ) : (
                <Row gutter={[24, 24]}>
                    {requestRows.length > 0 && (
                        <Section
                            title={t('Waiting for your decision')}
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
                            items={requestRows.slice(0, MAX_ITEMS).map((row) => (
                                <Flex key={row.key} align="center" gap="small">
                                    <UserAvatar
                                        user={row.requestedBy ?? undefined}
                                        color={token.colorPrimary}
                                        size="small"
                                    />
                                    <Flex vertical flex={1}>
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
                            title={t('Announcements')}
                            items={announcements
                                .slice(0, MAX_ITEMS)
                                .map((notification) => (
                                    <AnnouncementNotification
                                        key={notification.id}
                                        notification={notification}
                                        onAcknowledge={acknowledge}
                                        isAcknowledging={acknowledgingId === notification.id}
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
