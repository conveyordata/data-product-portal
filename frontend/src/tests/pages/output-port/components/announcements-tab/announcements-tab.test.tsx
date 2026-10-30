import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { AnnouncementsTab } from '@/pages/output-port/components/dataset-tabs/announcements-tab/announcements-tab.tsx';
import { type Announcement, AnnouncementType } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

const announcement: Announcement = {
    id: 'announcement-id',
    output_port_id: 'output-port-id',
    type: AnnouncementType.ActionNeeded,
    title: 'Daily Feature Engagement will be retired',
    message: 'Move your queries before 1 December. Guide: https://docs.example.com/migration.',
    author: null,
    created_at: '2026-10-26T10:00:00Z',
};

function mockApi(allowed: boolean, announcements: Announcement[]) {
    server.use(
        http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed })),
        http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId/announcements', () =>
            HttpResponse.json({ announcements }),
        ),
        http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId/input_ports/', () =>
            HttpResponse.json({ input_ports: [] }),
        ),
    );
}

describe('AnnouncementsTab', () => {
    it('shows announcements with their type and the links in their message', async () => {
        mockApi(false, [announcement]);

        renderWithProviders(<AnnouncementsTab dataProductId="data-product-id" outputPortId="output-port-id" />);

        expect(await screen.findByText(announcement.title)).toBeInTheDocument();
        expect(screen.getByRole('img', { name: 'Action needed' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'https://docs.example.com/migration' })).toHaveAttribute(
            'href',
            'https://docs.example.com/migration',
        );
    });

    it('filters announcements on title and message', async () => {
        const user = userEvent.setup();
        mockApi(false, [announcement, { ...announcement, id: 'other', title: 'Margin column added', message: 'New.' }]);

        renderWithProviders(<AnnouncementsTab dataProductId="data-product-id" outputPortId="output-port-id" />);
        await user.type(await screen.findByPlaceholderText('Search announcements by title or message'), 'december');

        expect(screen.getByText(announcement.title)).toBeInTheDocument();
        expect(screen.queryByText('Margin column added')).not.toBeInTheDocument();

        await user.clear(screen.getByPlaceholderText('Search announcements by title or message'));
        await user.type(screen.getByPlaceholderText('Search announcements by title or message'), 'nothing matches');
        expect(screen.getByText('No announcements match "nothing matches"')).toBeInTheDocument();
    });

    it.each([
        [true, true],
        [false, false],
    ])('shows post and delete actions when update access is %s', async (allowed, visible) => {
        mockApi(allowed, [announcement]);

        renderWithProviders(<AnnouncementsTab dataProductId="data-product-id" outputPortId="output-port-id" />);

        await screen.findByText(announcement.title);
        if (visible) {
            expect(await screen.findByText('New Announcement')).toBeInTheDocument();
            expect(screen.getByText('Delete')).toBeInTheDocument();
        } else {
            expect(screen.queryByText('New Announcement')).not.toBeInTheDocument();
            expect(screen.queryByText('Delete')).not.toBeInTheDocument();
        }
    });

    it('shows the consumer empty state', async () => {
        mockApi(false, []);

        renderWithProviders(<AnnouncementsTab dataProductId="data-product-id" outputPortId="output-port-id" />);

        expect(await screen.findByText('No announcements yet')).toBeInTheDocument();
        expect(screen.queryByText('New Announcement')).not.toBeInTheDocument();
    });
});
