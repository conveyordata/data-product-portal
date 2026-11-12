import { PostHogProvider } from '@posthog/react';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { NewDataProductForm } from '@/pages/cart/components/new-data-product-form.tsx';
import { DataProductVisibility, type GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
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

const savedProduct: GetDataProductResponse = {
    ...mockDataProducts[0],
    about: '',
    environments: [
        { environment_id: 'env-dev', environment: mockEnvironments[0], creation_date: '2026-10-12T10:00:00' },
    ],
};

function renderForm(mode: 'create' | 'edit') {
    return renderWithProviders(
        <PostHogProvider client={posthog}>
            <DataProductForm mode={mode} dataProductId={mode === 'edit' ? savedProduct.id : undefined} />
        </PostHogProvider>,
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

async function fillRequiredFields(user: ReturnType<typeof userEvent.setup>) {
    await user.type(screen.getByRole('textbox', { name: /^Name/ }), 'Environment test product');
    await user.click(screen.getByRole('combobox', { name: 'Type' }));
    await user.click(await screen.findByText('Reporting'));
    await user.click(screen.getByRole('combobox', { name: 'Status' }));
    await user.click(await screen.findByText('Draft'));
    await user.click(screen.getByRole('combobox', { name: /^Domain/ }));
    await user.click(await screen.findByText('Finance'));
    await user.type(screen.getByRole('textbox', { name: /^Description/ }), 'A product with saved environments.');
}

describe('DataProductForm', () => {
    beforeEach(() => {
        vi.spyOn(posthog, 'capture').mockImplementation(() => undefined);
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

    afterEach(() => {
        vi.restoreAllMocks();
        localStorage.clear();
    });

    describe.each([
        { flow: 'Product Studio', event: PosthogEvents.CREATE_DATA_PRODUCT_COMPLETED, cart: false },
        { flow: 'cart checkout', event: PosthogEvents.CART_CHECKOUT_COMPLETED_NEW_DATA_PRODUCT, cart: true },
    ])('$flow visibility tracking', ({ event, cart }) => {
        async function prepareForm(user: ReturnType<typeof userEvent.setup>, visibility: DataProductVisibility) {
            if (cart) {
                renderWithProviders(
                    <PostHogProvider client={posthog}>
                        <NewDataProductForm />
                    </PostHogProvider>,
                    {
                        routerProps: { initialEntries: ['/'] },
                        currentUser: mockUsers[0],
                        preloadedState: { cart: { DatasetIds: ['op-1'] } },
                    },
                );
            } else {
                renderForm('create');
            }
            await getEnvironmentPicker();
            await fillRequiredFields(user);
            if (cart) {
                await user.type(screen.getByRole('textbox', { name: 'Business justification' }), 'Analysis');
            }
            if (visibility === DataProductVisibility.Hidden) {
                await user.click(screen.getByText('Hidden'));
            }
        }

        async function submitHiddenForm(user: ReturnType<typeof userEvent.setup>) {
            await user.click(screen.getByRole('button', { name: 'Create' }));
            const confirmation = await screen.findByRole('tooltip');
            await user.click(within(confirmation).getByRole('button', { name: 'Create' }));
        }

        it.each([DataProductVisibility.Discoverable, DataProductVisibility.Hidden])(
            'tracks %s visibility after successful creation',
            async (visibility) => {
                const user = userEvent.setup();
                server.use(http.post('*/api/v2/data_products', () => HttpResponse.json({ id: 'created-product' })));
                await prepareForm(user, visibility);
                expect(posthog.capture).not.toHaveBeenCalled();
                if (visibility === DataProductVisibility.Hidden) {
                    await submitHiddenForm(user);
                } else {
                    await user.click(screen.getByRole('button', { name: 'Create' }));
                }
                await waitFor(() =>
                    expect(posthog.capture).toHaveBeenCalledExactlyOnceWith(
                        event,
                        cart ? { visibility, cartSize: 1 } : { visibility },
                    ),
                );
            },
        );

        it('does not track failed Hidden Data Product creation', async () => {
            const user = userEvent.setup();
            server.use(
                http.post('*/api/v2/data_products', () =>
                    HttpResponse.json({ detail: 'Creation failed' }, { status: 500 }),
                ),
            );
            await prepareForm(user, DataProductVisibility.Hidden);
            await submitHiddenForm(user);
            await screen.findByText(
                cart ? 'Failed to create Data Product. Please try again.' : 'Failed to create Data Product',
            );
            expect(posthog.capture).not.toHaveBeenCalled();
        });

        it('does not track cancelled Hidden Data Product creation', async () => {
            const user = userEvent.setup();
            const save = vi.fn(() => HttpResponse.json({ id: 'created-product' }));
            server.use(http.post('*/api/v2/data_products', save));
            await prepareForm(user, DataProductVisibility.Hidden);
            await user.click(screen.getByRole('button', { name: 'Create' }));
            const confirmation = await screen.findByRole('tooltip');
            await user.click(within(confirmation).getByRole('button', { name: 'Cancel' }));
            expect(save).not.toHaveBeenCalled();
            expect(posthog.capture).not.toHaveBeenCalled();
        });
    });

    it('prefills global defaults independently of Domain changes', async () => {
        const user = userEvent.setup();
        renderForm('create');
        const picker = await getEnvironmentPicker();
        expect(within(picker).getByText('Development')).toBeInTheDocument();
        expect(within(picker).getByText('Production')).toBeInTheDocument();
        expect(within(picker).queryByText('Test')).not.toBeInTheDocument();
        await user.click(screen.getByRole('combobox', { name: /^Domain/ }));
        await user.click(await screen.findByText('Finance'));
        expect(within(picker).getByText('Development')).toBeInTheDocument();
        expect(within(picker).queryByText('Test')).not.toBeInTheDocument();
    });

    it('requires at least one selected environment', async () => {
        const user = userEvent.setup();
        renderForm('create');
        const picker = await getEnvironmentPicker();
        await user.click(within(picker).getByLabelText('close-circle'));
        await user.click(screen.getByRole('button', { name: 'Create' }));
        expect(await screen.findByText('Please select at least one environment')).toBeInTheDocument();
    });

    it('sends selected environments when creating a Data Product', async () => {
        const user = userEvent.setup();
        const save = vi.fn();
        server.use(
            http.post('*/api/v2/data_products', async ({ request }) => {
                save(await request.json());
                return HttpResponse.json({ id: 'created-product' });
            }),
        );
        renderForm('create');
        await getEnvironmentPicker();
        await fillRequiredFields(user);
        await user.click(screen.getByRole('combobox', { name: /^Environments/ }));
        await user.click(await screen.findByText('Test'));
        await user.click(screen.getByRole('button', { name: 'Create' }));
        await waitFor(() =>
            expect(save).toHaveBeenCalledWith(
                expect.objectContaining({
                    environment_ids: ['env-dev', 'env-prd', 'env-tst'],
                }),
            ),
        );
    });

    it('locks saved environments even when they are no longer global defaults', async () => {
        const user = userEvent.setup();
        mockGetEnvironments(
            mockEnvironments.map((environment) => ({ ...environment, is_global: environment.id === 'env-prd' })),
        );
        renderForm('edit');
        const picker = await getEnvironmentPicker();
        expect(within(picker).getByText('Development')).toBeInTheDocument();
        expect(within(picker).queryByText('Production')).not.toBeInTheDocument();
        expect(within(picker).queryByLabelText('close')).not.toBeInTheDocument();
        expect(within(picker).queryByLabelText('close-circle')).not.toBeInTheDocument();
        await user.click(screen.getByRole('combobox', { name: /^Environments/ }));
        await user.keyboard('{Backspace}');
        expect(within(picker).getByText('Development')).toBeInTheDocument();
    });

    it('sends existing and newly added environments when editing', async () => {
        const user = userEvent.setup();
        const save = vi.fn();
        server.use(
            http.put('*/api/v2/data_products/dp-1', async ({ request }) => {
                save(await request.json());
                return HttpResponse.json({ id: 'dp-1' });
            }),
        );
        renderForm('edit');
        await getEnvironmentPicker();
        await user.click(screen.getByRole('combobox', { name: /^Environments/ }));
        await user.click(await screen.findByText('Test'));
        await user.click(screen.getByRole('button', { name: 'Save' }));
        await waitFor(() =>
            expect(save).toHaveBeenCalledWith(
                expect.objectContaining({
                    environment_ids: ['env-dev', 'env-tst'],
                }),
            ),
        );
    });

    it('explains why saved environments cannot be removed and keeps their options visible', async () => {
        const user = userEvent.setup();
        renderForm('edit');
        const picker = await getEnvironmentPicker();
        await user.hover(within(picker).getByText('Development'));
        expect(await screen.findByRole('tooltip')).toHaveTextContent(
            'Declared environments cannot be removed because resources may already be provisioned in them.',
        );
        await user.unhover(within(picker).getByText('Development'));
        await user.click(screen.getByRole('combobox', { name: /^Environments/ }));
        const savedOption = screen
            .getAllByText('Development')
            .find((element) => element.closest('.ant-select-item-option'));
        expect(savedOption?.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
    });

    it('explains when every available environment has been selected without hiding them', async () => {
        const user = userEvent.setup();
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
        await user.click(screen.getByRole('combobox', { name: /^Environments/ }));
        expect(await screen.findByText('All available environments are already selected')).toBeInTheDocument();
        for (const environment of mockEnvironments) {
            const option = screen
                .getAllByText(environment.name)
                .find((element) => element.closest('.ant-select-item-option'));
            expect(option?.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
        }
        expect(screen.queryByText('No matching environments')).not.toBeInTheDocument();
        await user.type(screen.getByRole('combobox', { name: /^Environments/ }), 'nonexistent');
        expect(await screen.findByText('No matching environments')).toBeInTheDocument();
        expect(screen.queryByText('All available environments are already selected')).not.toBeInTheDocument();
    });

    it('shows a plain no-match message when searching for an unconfigured environment', async () => {
        const user = userEvent.setup();
        renderForm('create');
        await getEnvironmentPicker();
        await user.type(screen.getByRole('combobox', { name: /^Environments/ }), 'nonexistent');
        expect(await screen.findByText('No matching environments')).toBeInTheDocument();
        expect(screen.queryByText('No environments are configured')).not.toBeInTheDocument();
    });
});
