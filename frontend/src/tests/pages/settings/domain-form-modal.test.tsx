import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { CreateDomainModal } from '@/pages/settings/components/settings-tabs/components/domain-table/domain-form-modal.component.tsx';
import { mockGetResourceNamesConstraints, mockResourceNamesValidate } from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('CreateDomainModal', () => {
    it('lets the user type a namespace when the name has no usable characters', async () => {
        mockGetResourceNamesConstraints();
        mockResourceNamesValidate();
        server.use(
            http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })),
            http.get('*/api/v2/resource_names/sanitize', () => HttpResponse.json({ resource_name: '' })),
        );
        const user = userEvent.setup();
        const { container } = renderWithProviders(<CreateDomainModal isOpen onClose={vi.fn()} mode="create" />);
        const namespace = () => container.ownerDocument.querySelector('[data-cy="namespace"]');

        expect(namespace()).toBeDisabled();
        await user.type(screen.getByLabelText('Name'), '!!!');

        await waitFor(() => expect(namespace()).toBeEnabled());
    });
});
