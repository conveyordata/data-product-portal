import { describe, expect, it } from 'vitest';
import { Notifications } from '@/components/notifications/notifications.tsx';
import {
    announcementNotification,
    mockUserNotifications,
    notifiedUser,
    requestNotification,
} from '@/tests/mocks/userNotifications.ts';
import { renderWithProviders, screen, userEvent, within } from '@/tests/test-utils.tsx';

async function openBell() {
    const user = userEvent.setup();
    renderWithProviders(<Notifications />, { routerProps: { initialEntries: ['/'] }, currentUser: notifiedUser });
    await user.hover(screen.getByRole('button', { name: 'bell' }));
    return screen.findByRole('tooltip', { hidden: true });
}

describe('Notifications', () => {
    it('shows requests before announcements', async () => {
        mockUserNotifications([
            announcementNotification('a1', 'op-1', 'Spend figures are being restated'),
            requestNotification('r1'),
        ]);

        const popover = await openBell();

        const requests = await within(popover).findByText('Requests');
        const announcements = within(popover).getByText('Announcements');
        expect(requests.compareDocumentPosition(announcements) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
        expect(within(popover).getByText('Marketing Attribution')).toBeInTheDocument();
    });

    it('shows an announcement with its type, title and Output Port linking to the Announcements tab', async () => {
        mockUserNotifications([announcementNotification('a1', 'op-1', 'Spend figures are being restated')]);

        const popover = await openBell();

        const title = await within(popover).findByText('Spend figures are being restated');
        expect(within(popover).getByText('Issue')).toBeInTheDocument();
        expect(within(popover).getByText('Output Port op-1')).toBeInTheDocument();
        expect(title.closest('a')).toHaveAttribute('href', expect.stringMatching(/op-1.*\?tab=announcements$/));
        expect(within(popover).getByRole('button', { name: 'Acknowledge' })).toBeInTheDocument();
        expect(within(popover).queryByText('Requests')).not.toBeInTheDocument();
    });
});
