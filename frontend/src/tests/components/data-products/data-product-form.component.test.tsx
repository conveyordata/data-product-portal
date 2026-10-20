import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import type { GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductLifecycles } from '@/tests/mocks/configurationDataProductLifecycles.ts';
import { mockGetDataProductTypes } from '@/tests/mocks/configurationDataProductTypes.ts';
import { mock_domains, mockGetDomains } from '@/tests/mocks/configurationDomains.ts';
import { mockEnvironments, mockGetEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { mockDataProductHttp, mockDataProducts } from '@/tests/mocks/dataProducts.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockGetTags } from '@/tests/mocks/tags.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor, within } from '@/tests/test-utils.tsx';
import { Prototype } from '@/types/roles';

vi.mock('@posthog/react', () => ({ usePostHog: () => ({ capture: vi.fn() }) }));

const savedProduct: GetDataProductResponse = {
    ...mockDataProducts[0],
    about: '',
    environments: [
        { environment_id: 'env-dev', environment: mockEnvironments[0], creation_date: '2026-10-12T10:00:00' },
    ],
};

function renderForm(mode: 'create' | 'edit') {
    return renderWithProviders(
        <DataProductForm mode={mode} dataProductId={mode === 'edit' ? savedProduct.id : undefined} />,
        {
            routerProps: { initialEntries: ['/'] },
            currentUser: mockUsers[0],
        },
    );
}

async function getEnvironmentPicker() {
    const input = await screen.findByRole('combobox', { name: /^Environments/ });
    await waitFor(() => expect(input).toBeEnabled());
    return input.closest('[data-cy="data-product-environments"]') as HTMLElement;
}

async function fillRequiredFields() {
    await userEvent.type(screen.getByRole('textbox', { name: /^Name/ }), 'Environment test product');
    await userEvent.click(screen.getByRole('combobox', { name: 'Type' }));
    await userEvent.click(await screen.findByText('Reporting'));
    await userEvent.click(screen.getByRole('combobox', { name: 'Status' }));
    await userEvent.click(await screen.findByText('Draft'));
    await userEvent.click(screen.getByRole('combobox', { name: /^Domain/ }));
    await userEvent.click(await screen.findByText('Finance'));
    await userEvent.type(screen.getByRole('textbox', { name: /^Description/ }), 'A product with saved environments.');
}

describe('DataProductForm environments', () => {
    beforeEach(() => {
        allowAllAuth();
        mockGetEnvironments();
        mockGetDomains(mock_domains);
        mockGetDataProductTypes();
        mockDataProductLifecycles();
        mockUsersHttp(mockUsers);
        mockGetTags();
        mockGetResourceNamesConstraints();
        mockResourceNamesSanitize();
        mockResourceNamesValidate();
        mockDataProductHttp(savedProduct.id, savedProduct);
        server.use(
            http.get('*/api/v2/authz/role_assignments/data_product', () =>
                HttpResponse.json({
                    role_assignments: [{ role: { prototype: Prototype.OWNER }, user: mockUsers[0] }],
                }),
            ),
        );
    });

    it('prefills global defaults independently of Domain changes', async () => {
        renderForm('create');
        const picker = await getEnvironmentPicker();
        expect(within(picker).getByText('Development')).toBeInTheDocument();
        expect(within(picker).getByText('Production')).toBeInTheDocument();
        expect(within(picker).queryByText('Test')).not.toBeInTheDocument();
        await userEvent.click(screen.getByRole('combobox', { name: /^Domain/ }));
        await userEvent.click(await screen.findByText('Finance'));
        expect(within(picker).getByText('Development')).toBeInTheDocument();
        expect(within(picker).queryByText('Test')).not.toBeInTheDocument();
    });

    it('requires at least one selected environment', async () => {
        renderForm('create');
        const picker = await getEnvironmentPicker();
        await userEvent.click(within(picker).getByLabelText('close-circle'));
        await userEvent.click(screen.getByRole('button', { name: 'Create' }));
        expect(await screen.findByText('Please select at least one environment')).toBeInTheDocument();
    });

    it('sends selected environments when creating a Data Product', async () => {
        const save = vi.fn();
        server.use(
            http.post('*/api/v2/data_products', async ({ request }) => {
                save(await request.json());
                return HttpResponse.json({ id: 'created-product' });
            }),
        );
        renderForm('create');
        await getEnvironmentPicker();
        await fillRequiredFields();
        await userEvent.click(screen.getByRole('combobox', { name: /^Environments/ }));
        await userEvent.click(await screen.findByText('Test'));
        await userEvent.click(screen.getByRole('button', { name: 'Create' }));
        await waitFor(() =>
            expect(save).toHaveBeenCalledWith(
                expect.objectContaining({
                    environment_ids: ['env-dev', 'env-prd', 'env-tst'],
                }),
            ),
        );
    });

    it('locks saved environments even when they are no longer global defaults', async () => {
        mockGetEnvironments(
            mockEnvironments.map((environment) => ({ ...environment, is_global: environment.id === 'env-prd' })),
        );
        renderForm('edit');
        const picker = await getEnvironmentPicker();
        expect(within(picker).getByText('Development')).toBeInTheDocument();
        expect(within(picker).queryByText('Production')).not.toBeInTheDocument();
        expect(within(picker).queryByLabelText('close')).not.toBeInTheDocument();
        expect(within(picker).queryByLabelText('close-circle')).not.toBeInTheDocument();
        await userEvent.click(screen.getByRole('combobox', { name: /^Environments/ }));
        await userEvent.keyboard('{Backspace}');
        expect(within(picker).getByText('Development')).toBeInTheDocument();
    });

    it('sends existing and newly added environments when editing', async () => {
        const save = vi.fn();
        server.use(
            http.put('*/api/v2/data_products/dp-1', async ({ request }) => {
                save(await request.json());
                return HttpResponse.json({ id: 'dp-1' });
            }),
        );
        renderForm('edit');
        await getEnvironmentPicker();
        await userEvent.click(screen.getByRole('combobox', { name: /^Environments/ }));
        await userEvent.click(await screen.findByText('Test'));
        await userEvent.click(screen.getByRole('button', { name: 'Save' }));
        await waitFor(() =>
            expect(save).toHaveBeenCalledWith(
                expect.objectContaining({
                    environment_ids: ['env-dev', 'env-tst'],
                }),
            ),
        );
    });

    it('explains why saved environments cannot be removed and keeps their options visible', async () => {
        renderForm('edit');
        const picker = await getEnvironmentPicker();
        await userEvent.hover(within(picker).getByText('Development'));
        expect(await screen.findByRole('tooltip')).toHaveTextContent(
            'Declared environments cannot be removed because resources may already be provisioned in them.',
        );
        await userEvent.unhover(within(picker).getByText('Development'));
        await userEvent.click(screen.getByRole('combobox', { name: /^Environments/ }));
        const savedOption = screen
            .getAllByText('Development')
            .find((element) => element.closest('.ant-select-item-option'));
        expect(savedOption?.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
    });

    it('explains when every available environment has been selected without hiding them', async () => {
        mockDataProductHttp(savedProduct.id, {
            ...savedProduct,
            environments: mockEnvironments.map((environment) => ({
                environment_id: environment.id,
                environment,
                creation_date: '2026-10-12T10:00:00',
            })),
        });
        renderForm('edit');
        await getEnvironmentPicker();
        await userEvent.click(screen.getByRole('combobox', { name: /^Environments/ }));
        expect(await screen.findByText('All available environments are already selected')).toBeInTheDocument();
        for (const environment of mockEnvironments) {
            const option = screen
                .getAllByText(environment.name)
                .find((element) => element.closest('.ant-select-item-option'));
            expect(option?.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
        }
        expect(screen.queryByText('No matching environments')).not.toBeInTheDocument();
        await userEvent.type(screen.getByRole('combobox', { name: /^Environments/ }), 'nonexistent');
        expect(await screen.findByText('No matching environments')).toBeInTheDocument();
        expect(screen.queryByText('All available environments are already selected')).not.toBeInTheDocument();
    });

    it('shows a plain no-match message when searching for an unconfigured environment', async () => {
        renderForm('create');
        await getEnvironmentPicker();
        await userEvent.type(screen.getByRole('combobox', { name: /^Environments/ }), 'nonexistent');
        expect(await screen.findByText('No matching environments')).toBeInTheDocument();
        expect(screen.queryByText('No environments are configured')).not.toBeInTheDocument();
    });
});
