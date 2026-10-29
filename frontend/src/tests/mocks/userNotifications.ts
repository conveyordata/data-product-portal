import { HttpResponse, http } from 'msw';
import {
    AnnouncementType,
    EventEntityType,
    type GetEventHistoryResponseItem,
    type GetUserNotificationsResponse,
    type GetUserNotificationsResponseItem,
    OutputPortAccessFunction,
    OutputPortStatus,
    type User,
} from '@/store/api/services/generated/usersNotificationsApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { EventType } from '@/types/events/event-types.ts';

export const notifiedUser: User = {
    id: 'consumer-user',
    email: 'consumer@example.com',
    external_id: 'consumer-user',
    first_name: 'Lena',
    last_name: 'Wouters',
    has_seen_tour: true,
    can_become_admin: false,
};

function notification(event: GetEventHistoryResponseItem): GetUserNotificationsResponseItem {
    return {
        id: `notification-${event.id}`,
        event_id: event.id,
        user_id: notifiedUser.id,
        event,
        user: notifiedUser,
    };
}

export function announcementNotification(
    id: string,
    outputPortId: string,
    title: string,
    type: AnnouncementType = AnnouncementType.Warning,
    createdOn = '2026-10-26T10:00:00',
) {
    return notification({
        id,
        name: EventType.ANNOUNCEMENT_CREATED,
        subject_id: outputPortId,
        subject_type: EventEntityType.OutputPort,
        target_id: `announcement-${id}`,
        target_type: EventEntityType.Announcement,
        actor_id: 'producer-user',
        created_on: createdOn,
        output_port: {
            id: outputPortId,
            name: `Output Port ${outputPortId}`,
            namespace: outputPortId,
            description: '',
            status: OutputPortStatus.Active,
            access_type: {
                id: 'access-type',
                name: 'Unrestricted',
                access_function: OutputPortAccessFunction.Unrestricted,
            },
            data_product_id: 'producer-data-product',
            tags: [],
            access_modes: [],
        },
        announcement: {
            id: `announcement-${id}`,
            output_port_id: outputPortId,
            type,
            title,
            message: 'Details on https://status.example.com/incident',
            author: null,
            created_at: '2026-10-26T10:00:00Z',
        },
    });
}

export function requestNotification(id: string) {
    return notification({
        id,
        name: EventType.DATA_PRODUCT_CREATED,
        subject_id: 'data-product',
        subject_type: EventEntityType.DataProduct,
        actor_id: 'producer-user',
        deleted_subject_identifier: 'Marketing Attribution',
        created_on: '2026-10-26T10:00:00',
    });
}

export function mockUserNotifications(notifications: GetUserNotificationsResponseItem[]) {
    server.use(
        http.get('*/api/v2/users/current/notifications', () =>
            HttpResponse.json({ notifications } satisfies GetUserNotificationsResponse),
        ),
    );
}
