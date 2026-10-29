import { delay, HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { HomeNotifications } from '@/pages/home/components/home-notifications/home-notifications.tsx';
import { AnnouncementType } from '@/store/api/services/generated/usersNotificationsApi.ts';
import { server } from '@/tests/mocks/server.ts';
import {
    announcementNotification,
    mockUserNotifications,
    notifiedUser,
    requestNotification,
} from '@/tests/mocks/userNotifications.ts';
import { mockUserPendingActions, roleAssignmentRequest } from '@/tests/mocks/userPendingActions.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

function renderBlock() {
    renderWithProviders(<HomeNotifications />, { routerProps: { initialEntries: ['/'] }, currentUser: notifiedUser });
}

describe('HomeNotifications', () => {
    it('shows requests before announcements with a View all link to the Pending Requests tab', async () => {
        mockUserPendingActions([roleAssignmentRequest('r1', 'Marketing Attribution')]);
        mockUserNotifications([announcementNotification('a1', 'op-1', 'Spend figures are being restated')]);

        renderBlock();

        const requests = await screen.findByText('Waiting for your decision (1)');
        const announcements = screen.getByText('Announcements');
        expect(requests.compareDocumentPosition(announcements) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
        expect(screen.getByText(/requests the role role for Marketing Attribution/)).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /View all/ })).toHaveAttribute('href', '/studio?tab=pending-requests');
    });

    it('shows at most five items per section', async () => {
        mockUserPendingActions(
            Array.from({ length: 7 }, (_, i) => roleAssignmentRequest(`r${i}`, `Data Product ${i}`)),
        );
        mockUserNotifications(
            Array.from({ length: 7 }, (_, i) => announcementNotification(`a${i}`, `op-${i}`, `Title ${i}`)),
        );

        renderBlock();

        expect(await screen.findAllByRole('button', { name: /Review/ })).toHaveLength(5);
        expect(screen.getByText('Waiting for your decision (7)')).toBeInTheDocument();
        expect(screen.getAllByRole('button', { name: 'Acknowledge' })).toHaveLength(5);
    });

    it('still shows announcements when requests fail to load', async () => {
        server.use(http.get('*/api/v2/users/current/pending_actions', () => new HttpResponse(null, { status: 500 })));
        mockUserNotifications([announcementNotification('a1', 'op-1', 'Spend figures are being restated')]);

        renderBlock();

        expect(await screen.findByText('Spend figures are being restated')).toBeInTheDocument();
    });

    it('shows announcements while requests are still loading', async () => {
        server.use(
            http.get('*/api/v2/users/current/pending_actions', async () => {
                await delay('infinite');
                return HttpResponse.json({ pending_actions: [] });
            }),
        );
        mockUserNotifications([announcementNotification('a1', 'op-1', 'Spend figures are being restated')]);

        renderBlock();

        expect(await screen.findByText('Spend figures are being restated')).toBeInTheDocument();
    });

    it('orders announcements by urgency, then newest first', async () => {
        mockUserPendingActions([]);
        mockUserNotifications([
            announcementNotification('a1', 'op-1', 'General news', AnnouncementType.Info, '2026-10-27T10:00:00'),
            announcementNotification('a2', 'op-2', 'Old issue', AnnouncementType.ActionNeeded, '2026-10-20T10:00:00'),
            announcementNotification('a3', 'op-3', 'Maintenance', AnnouncementType.Warning),
            announcementNotification('a4', 'op-4', 'New issue', AnnouncementType.ActionNeeded, '2026-10-25T10:00:00'),
        ]);

        renderBlock();

        await screen.findByText('General news');
        const titles = screen
            .getAllByText(/General news|Old issue|Maintenance|New issue/)
            .map((element) => element.textContent);
        expect(titles).toEqual(['New issue', 'Old issue', 'Maintenance', 'General news']);
        expect(screen.queryByText(/Waiting for your decision/)).not.toBeInTheDocument();
    });

    it('acknowledges an announcement through the notifications endpoint', async () => {
        const user = userEvent.setup();
        let acknowledged: string | undefined;
        mockUserPendingActions([]);
        mockUserNotifications([announcementNotification('a1', 'op-1', 'Spend figures are being restated')]);
        server.use(
            http.delete('*/api/v2/users/current/notifications/:id', ({ params }) => {
                acknowledged = String(params.id);
                return new HttpResponse(null, { status: 204 });
            }),
        );

        renderBlock();
        await user.click(await screen.findByRole('button', { name: 'Acknowledge' }));

        await waitFor(() => expect(acknowledged).toBe('notification-a1'));
    });

    it('acknowledges all announcements but no other notifications', async () => {
        const user = userEvent.setup();
        const acknowledged: string[] = [];
        mockUserPendingActions([]);
        mockUserNotifications([
            ...Array.from({ length: 7 }, (_, i) => announcementNotification(`a${i}`, `op-${i}`, `Title ${i}`)),
            requestNotification('r1'),
        ]);
        server.use(
            http.delete('*/api/v2/users/current/notifications/:id', ({ params }) => {
                acknowledged.push(String(params.id));
                return new HttpResponse(null, { status: 204 });
            }),
        );

        renderBlock();
        await user.click(await screen.findByRole('button', { name: 'Acknowledge all' }));

        await waitFor(() => expect(acknowledged).toHaveLength(7));
        expect(acknowledged.sort()).toEqual(Array.from({ length: 7 }, (_, i) => `notification-a${i}`).sort());
    });

    it('renders nothing when there are no requests or announcements', async () => {
        let loaded = false;
        mockUserPendingActions([]);
        server.use(
            http.get('*/api/v2/users/current/notifications', () => {
                loaded = true;
                return HttpResponse.json({ notifications: [] });
            }),
        );

        const { container } = renderWithProviders(<HomeNotifications />, {
            routerProps: { initialEntries: ['/'] },
            currentUser: notifiedUser,
        });

        await waitFor(() => expect(loaded).toBe(true));
        expect(container).toBeEmptyDOMElement();
    });

    it('shows the full message, type and Output Port in the Read more popover', async () => {
        const user = userEvent.setup();
        mockUserPendingActions([]);
        mockUserNotifications([announcementNotification('a1', 'op-1', 'Spend figures are being restated')]);

        renderBlock();
        await user.click(await screen.findByRole('button', { name: 'Read more' }));

        expect(await screen.findByRole('link', { name: 'https://status.example.com/incident' })).toHaveAttribute(
            'href',
            'https://status.example.com/incident',
        );
        expect(screen.getByText('Warning')).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Output Port op-1' })).toHaveAttribute(
            'href',
            expect.stringMatching(/op-1.*\?tab=announcements$/),
        );
    });
});
