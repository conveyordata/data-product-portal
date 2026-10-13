import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { HistoryTab } from '@/components/history/history-tab.tsx';
import { Notifications } from '@/components/notifications/notifications.tsx';
import {
    EventEntityType,
    type GetEventHistoryResponseItem,
    type GetUserNotificationsResponse,
    type User,
} from '@/store/api/services/generated/usersNotificationsApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, within } from '@/tests/test-utils.tsx';
import { EventReferenceEntity } from '@/types/events/event-reference-entity.ts';
import { EventType } from '@/types/events/event-types.ts';

const currentUser: User = {
    id: 'live-user',
    email: 'live@example.com',
    external_id: 'live-user',
    first_name: 'Alex',
    last_name: 'Reader',
    has_seen_tour: true,
    can_become_admin: false,
};

const deletedActorEvent: GetEventHistoryResponseItem = {
    id: 'deleted-actor-event',
    name: EventType.DATA_PRODUCT_CREATED,
    subject_id: 'product-1',
    subject_type: EventEntityType.DataProduct,
    actor_id: 'deleted-user',
    actor: null,
    deleted_actor_identifier: 'deleted@example.com',
    created_on: '2026-10-07T12:00:00',
};

describe('Deleted event actors', () => {
    it('shows the saved email for a null actor in history alongside live actors', () => {
        renderWithProviders(
            <HistoryTab
                id={deletedActorEvent.subject_id}
                type={EventReferenceEntity.DataProduct}
                history={[
                    deletedActorEvent,
                    {
                        ...deletedActorEvent,
                        id: 'live-actor-event',
                        actor_id: currentUser.id,
                        actor: currentUser,
                        deleted_actor_identifier: null,
                    },
                ]}
                isFetching={false}
            />,
            { routerProps: { initialEntries: ['/'] } },
        );

        expect(screen.getByRole('cell', { name: 'deleted@example.com' })).toBeVisible();
        expect(screen.getByRole('cell', { name: currentUser.email })).toBeVisible();
    });

    it('shows saved emails in notifications and groups deleted actors by their retained IDs', async () => {
        const events: GetEventHistoryResponseItem[] = [
            deletedActorEvent,
            {
                ...deletedActorEvent,
                id: 'same-actor-event',
                name: EventType.DATA_PRODUCT_UPDATED,
            },
            {
                ...deletedActorEvent,
                id: 'other-deleted-actor-event',
                actor_id: 'other-deleted-user',
                deleted_actor_identifier: 'other-deleted@example.com',
            },
            {
                ...deletedActorEvent,
                id: 'live-actor-event',
                actor_id: currentUser.id,
                actor: currentUser,
                deleted_actor_identifier: null,
            },
        ];
        server.use(
            http.get('*/api/v2/users/current/notifications', () =>
                HttpResponse.json({
                    notifications: events.map((event) => ({
                        id: `notification-${event.id}`,
                        event_id: event.id,
                        user_id: currentUser.id,
                        event,
                        user: currentUser,
                    })),
                } satisfies GetUserNotificationsResponse),
            ),
        );
        const user = userEvent.setup();
        renderWithProviders(<Notifications />, {
            routerProps: { initialEntries: ['/'] },
            currentUser,
        });

        const bellButton = screen.getByRole('button', { name: 'bell' });
        await user.hover(bellButton);

        const popover = await screen.findByRole('tooltip', { hidden: true });
        expect(bellButton).toHaveAttribute('aria-describedby', popover.id);
        expect(await within(popover).findAllByText(/^deleted@example\.com,/)).toHaveLength(1);
        expect(within(popover).getByText(/^other-deleted@example\.com,/)).toBeInTheDocument();
        expect(within(popover).getByText(/^Alex Reader,/)).toBeInTheDocument();
    });
});
