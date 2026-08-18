import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import AccessDurations from '@/pages/settings/components/settings-tabs/access-policy-tab/access-durations.tsx';
import { mockAccessDurations, mockAccessDurationsGet } from '@/tests/mocks/configurationAccessDurations.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('AccessDurations', () => {
    it('auto-saves changes after a brief idle period and hides the save button', async () => {
        mockAccessDurationsGet();
        const mockSavedAccessDurations = [
            mockAccessDurations[0],
            {
                ...mockAccessDurations[1],
                is_default: false,
            },
        ];
        const updateAccessDurationHandler = vi.fn(() => HttpResponse.json(mockSavedAccessDurations));
        server.use(
            http.put('*/api/v2/configuration/access_durations/:abstractDataProductType', updateAccessDurationHandler),
        );

        renderWithProviders(<AccessDurations />);

        const [firstCheckbox] = await screen.findAllByRole('checkbox');
        await userEvent.click(firstCheckbox);

        await waitFor(
            () => {
                expect(updateAccessDurationHandler).toHaveBeenCalledTimes(2);
            },
            { timeout: 10000 },
        );
    });
});
