import { describe, expect, it } from 'vitest';
import AccessDurations from '@/pages/settings/components/settings-tabs/access-policy-tab/access-durations.tsx';
import {
    mockAccessDurations,
    mockAccessDurationsGet,
    mockUpdateAccessDuration,
} from '@/tests/mocks/configurationAccessDurations.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('AccessDurations', () => {
    it('disables save when there are no unsaved changes', async () => {
        mockAccessDurationsGet();
        const mockSavedAccessDurations = [
            mockAccessDurations[0],
            {
                ...mockAccessDurations[1],
                is_default: false,
            },
        ];
        mockUpdateAccessDuration(mockSavedAccessDurations);
        renderWithProviders(<AccessDurations />);

        const saveButton = await screen.findByRole('button', { name: 'Save' });

        await waitFor(() => {
            expect(saveButton).toBeDisabled();
        });

        const [firstCheckbox] = await screen.findAllByRole('checkbox');

        await userEvent.click(firstCheckbox);

        await waitFor(() => {
            expect(saveButton).toBeEnabled();
        });

        await userEvent.click(firstCheckbox);

        await waitFor(() => {
            expect(saveButton).toBeDisabled();
        });

        await userEvent.click(firstCheckbox);
        mockAccessDurationsGet(mockSavedAccessDurations);
        await userEvent.click(saveButton);

        await waitFor(() => {
            expect(saveButton).toBeDisabled();
        });
    });
});
