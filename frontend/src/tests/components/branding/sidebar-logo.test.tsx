import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { SidebarLogo } from '@/components/branding/sidebar-logo/sidebar-logo.tsx';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, waitFor } from '../../test-utils';

describe('SidebarLogo', () => {
    it('shows the configured portal name in the sidebar and the browser tab', async () => {
        server.use(
            http.get('*/api/v2/configuration/theme_settings', () => HttpResponse.json({ portal_name: 'Acme Portal' })),
        );

        renderWithProviders(<SidebarLogo />);

        expect(await screen.findByText('Acme Portal')).toBeInTheDocument();
        await waitFor(() => expect(document.title).toBe('Acme Portal'));
    });
});
