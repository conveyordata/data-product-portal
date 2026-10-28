import { beforeAll, describe, expect, it } from 'vitest';
import { NewAnnouncementsTag } from '@/components/announcements/new-announcements-tag.tsx';
import i18n from '@/tests/i18n.ts';
import {
    announcementNotification,
    mockUserNotifications,
    requestNotification,
} from '@/tests/mocks/userNotifications.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';
import translations from '../../../../public/locales/en/translation.json';

const ROUTER = { routerProps: { initialEntries: ['/'] } };

describe('NewAnnouncementsTag', () => {
    beforeAll(() => {
        const key = '{{count}} new announcements_one';
        i18n.addResource('en', 'translation', key, translations[key]);
    });

    it.each([
        [1, '1 new announcement'],
        [2, '2 new announcements'],
    ])('shows %i unacknowledged announcements', async (count, label) => {
        mockUserNotifications([
            ...Array.from({ length: count }, (_, i) => announcementNotification(`a${i}`, 'op-1', `Title ${i}`)),
            announcementNotification('other', 'op-2', 'Other Output Port'),
            requestNotification('r1'),
        ]);

        renderWithProviders(<NewAnnouncementsTag outputPortId="op-1" dataProductId="dp-1" />, ROUTER);

        const tag = await screen.findByText(label);
        expect(tag.closest('a')).toHaveAttribute('href', expect.stringMatching(/op-1.*\?tab=announcements$/));
    });

    it('shows nothing for an Output Port without unacknowledged announcements', async () => {
        mockUserNotifications([
            announcementNotification('other', 'op-2', 'Other Output Port'),
            requestNotification('r1'),
        ]);

        renderWithProviders(
            <>
                <NewAnnouncementsTag outputPortId="op-1" dataProductId="dp-1" />
                <NewAnnouncementsTag outputPortId="op-2" dataProductId="dp-1" />
            </>,
            ROUTER,
        );

        expect(await screen.findAllByText(/new announcement/)).toHaveLength(1);
        expect(screen.getByText('1 new announcement').closest('a')).toHaveAttribute(
            'href',
            expect.stringMatching(/op-2/),
        );
    });
});
