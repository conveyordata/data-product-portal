import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { CreateDomainModal } from '@/pages/settings/components/settings-tabs/components/domain-table/domain-form-modal.component.tsx';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('CreateDomainModal', () => {
    it('lets the user type a namespace when the name has no usable characters', async () => {
        mockGetResourceNamesConstraints();
        mockResourceNamesValidate();
        mockResourceNamesSanitize('');
        server.use(http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })));
        const user = userEvent.setup();
        renderWithProviders(<CreateDomainModal isOpen onClose={vi.fn()} mode="create" />);
        const namespace = () => document.querySelector('[data-cy="namespace"]');

        expect(namespace()).toBeDisabled();
        await user.type(screen.getByLabelText('Name'), '!!!');

        await waitFor(() => expect(namespace()).toBeEnabled());
    });

    it('keeps suggesting the namespace when the user starts typing after the form settled', async () => {
        mockGetResourceNamesConstraints();
        mockResourceNamesValidate();
        mockResourceNamesSanitize(undefined, 300);
        server.use(http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })));
        const user = userEvent.setup();
        renderWithProviders(<CreateDomainModal isOpen onClose={vi.fn()} mode="create" />);
        const namespace = () => document.querySelector<HTMLInputElement>('[data-cy="namespace"]');

        await new Promise((resolve) => setTimeout(resolve, 700));
        await user.type(screen.getByLabelText('Name'), 'sales');

        await waitFor(() => expect(namespace()?.value).toBe('sales'));
        expect(namespace()).toBeDisabled();
    });

    it('blocks creating until the namespace for the current name has been generated', async () => {
        mockGetResourceNamesConstraints();
        mockResourceNamesValidate();
        mockResourceNamesSanitize();
        server.use(http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })));
        const user = userEvent.setup();
        renderWithProviders(<CreateDomainModal isOpen onClose={vi.fn()} mode="create" />);
        const create = screen.getByRole('button', { name: 'Create' });

        await user.type(screen.getByLabelText('Name'), 'sales');
        expect(create).toBeDisabled();

        await waitFor(() => {
            expect(create).toBeEnabled();
            expect(document.querySelector<HTMLInputElement>('[data-cy="namespace"]')?.value).toBe('sales');
        });
    });
});
