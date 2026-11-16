import { HttpResponse, http } from 'msw';
import { Link, Route, Routes } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import Cart from '@/pages/cart/cart.page.tsx';
import {
    AccessDurationType,
    type GetOutputPortAccessDurationsResponse,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { ResourceNameValidityType } from '@/store/api/services/generated/resourceNamesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductLifecycles } from '@/tests/mocks/configurationDataProductLifecycles.ts';
import { mockGetDataProductTypes } from '@/tests/mocks/configurationDataProductTypes.ts';
import { mockGetDomains } from '@/tests/mocks/configurationDomains.ts';
import { mockGetEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { mockDataProductOutputPorts } from '@/tests/mocks/dataProductOutputPorts.ts';
import { mockDataProductInputPorts, mockDataProducts, mockDataProductsHttp } from '@/tests/mocks/dataProducts.ts';
import { mockExplorationInputPorts, mockExplorations, mockExplorationsHttp } from '@/tests/mocks/explorations.ts';
import { mockOutputPortsSearch } from '@/tests/mocks/outputPortsSearch.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockGetTags } from '@/tests/mocks/tags.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users.ts';
import { act, renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

afterEach(() => {
    localStorage.clear();
});

const createNewExploration = async (user: ReturnType<typeof userEvent.setup>) => {
    const existingChoice = await screen.findByText('Create a new Exploration');
    await user.click(existingChoice);
};

describe('Cart', () => {
    beforeEach(() => {
        const permanent = { access_duration_type: AccessDurationType.Permanent, days: 0 };
        server.use(
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:id/access_durations', ({ params }) =>
                HttpResponse.json<GetOutputPortAccessDurationsResponse>({
                    id: String(params.id),
                    data_product_access_duration: permanent,
                    exploration_access_duration: permanent,
                }),
            ),
        );
    });
    const selectDataProducts = async (user: ReturnType<typeof userEvent.setup>) => {
        const dataProductChoice = await screen.findByText('I want to build Data Products');
        await user.click(dataProductChoice);
    };
    const selectExplorations = async (user: ReturnType<typeof userEvent.setup>) => {
        const explorationsChoice = await screen.findByText('I want to explore this data');
        await user.click(explorationsChoice);
    };
    const selectExistingExplorations = async (user: ReturnType<typeof userEvent.setup>) => {
        const existingChoice = await screen.findByText('Select an existing Exploration');
        await user.click(existingChoice);
    };
    describe('Empty cart page', () => {
        it('Should show a message to direct to the Marketplace', async () => {
            mockOutputPortsSearch([]);
            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                currentUser: mockUsers[0],
            });

            await screen.findByText(/Your cart is empty/);
        });
    });
    describe('Cart should support existing data products', () => {
        const selectExistingDataProducts = async (user: ReturnType<typeof userEvent.setup>) => {
            const existingChoice = await screen.findByText('Select an existing Data Product');
            await user.click(existingChoice);
        };
        it('should allow users to select an existing data product', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            // Mock the output ports search (cart items)
            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockDataProductsHttp();
            mockDataProductInputPorts(mockDataProducts[0].id, []);
            mockDataProductOutputPorts(mockDataProducts[0].id, []);

            const submitHandler = vi.fn(() => HttpResponse.json({}));
            server.use(http.post(`*/api/v2/data_products/${mockDataProducts[0].id}/input_ports`, submitHandler));

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await selectExistingDataProducts(user);

            const selectDataProduct1 = await screen.findByText(mockDataProducts[0].name);
            await user.click(selectDataProduct1);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await user.type(justificationTextArea, 'I need this data for my analysis.');

            const submitButton = await screen.findByText('Submit access requests');
            await user.click(submitButton);

            // Assert the submit API was called
            await waitFor(() => {
                expect(submitHandler).toHaveBeenCalled();
            });
        });

        it('When selecting an existing data product with overlap in input ports and the cart it should show a warning', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockDataProductsHttp();
            mockDataProductInputPorts(mockDataProducts[0].id);
            mockDataProductOutputPorts(mockDataProducts[0].id, []);

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await selectExistingDataProducts(user);

            const selectDataProduct1 = await screen.findByText(mockDataProducts[0].name);
            await user.click(selectDataProduct1);

            await waitFor(() => {
                expect(
                    screen.getByText(
                        /Output Ports in the cart, for which the selected Data Product already has access/,
                    ),
                ).toBeInTheDocument();
            });
        });

        it('When selecting an existing data product with overlap in output ports and the cart should show a warning', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockDataProductsHttp();
            mockDataProductInputPorts(mockDataProducts[0].id, []);
            mockDataProductOutputPorts(mockDataProducts[0].id);

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await selectExistingDataProducts(user);

            const selectDataProduct1 = await screen.findByText(mockDataProducts[0].name);
            await user.click(selectDataProduct1);

            await waitFor(() => {
                expect(
                    screen.getByText(/Output Ports, that are part of your selected Data Product/),
                ).toBeInTheDocument();
            });
        });
    });

    describe('Cart should support creating a new data product', () => {
        beforeEach(() => mockGetEnvironments());

        const createNewDataProduct = async (user: ReturnType<typeof userEvent.setup>) => {
            const existingChoice = await screen.findByText('Create a new Data Product');
            await user.click(existingChoice);
        };

        const fillRequiredDataProductFields = async (
            user: ReturnType<typeof userEvent.setup>,
            {
                name = 'My New Data Product',
                description = 'A detailed description of the data product.',
                hidden = false,
                justification = 'I need this data for my analysis.',
            } = {},
        ) => {
            const nameInput = await screen.findByRole('textbox', { name: /name/i });
            await user.type(nameInput, name);

            if (hidden) {
                await user.click(screen.getByText('Hidden'));
                await waitFor(() => {
                    expect(
                        screen.getByText(/Only use a hidden Data Product when it's really required/i),
                    ).toBeInTheDocument();
                });
            }

            await user.click(screen.getByRole('combobox', { name: /type/i }));
            await user.click(await screen.findByText('Reporting'));

            await user.click(screen.getByRole('combobox', { name: /status/i }));
            await user.click(await screen.findByText('Draft'));

            await user.click(screen.getByRole('combobox', { name: /domain/i }));
            await user.click(await screen.findByText('Finance'));

            await user.type(screen.getByRole('textbox', { name: /description/i }), description);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await user.type(justificationTextArea, justification);
        };

        it('Should succeed when filling in the form completely', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetTags();
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize();
            mockResourceNamesValidate();
            mockGetDataProductTypes();
            mockDataProductLifecycles();
            mockGetDomains();

            const createdDataProductId = 'new-dp-id';
            const createHandler = vi.fn(() => HttpResponse.json({ id: createdDataProductId }));
            server.use(http.post('*/api/v2/data_products', createHandler));

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await createNewDataProduct(user);
            await fillRequiredDataProductFields(user);

            const submitButton = await screen.findByText('Create');
            await user.click(submitButton);

            await waitFor(() => {
                expect(createHandler).toHaveBeenCalled();
            });
        });

        it('lets the user type a namespace when the name has no usable characters', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetTags();
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize('');
            mockResourceNamesValidate();
            mockGetDataProductTypes();
            mockDataProductLifecycles();
            mockGetDomains();

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: ['op-1'] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await createNewDataProduct(user);
            const namespace = () => document.querySelector('[data-cy="namespace"]');
            expect(namespace()).toBeDisabled();

            await user.type(await screen.findByRole('textbox', { name: /name/i }), '!!!');

            await waitFor(() => expect(namespace()).toBeEnabled());
        });

        it('keeps suggesting the namespace when the user starts typing after the form settled', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetTags();
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize(undefined, 300);
            mockResourceNamesValidate();
            mockGetDataProductTypes();
            mockDataProductLifecycles();
            mockGetDomains();

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: ['op-1'] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await createNewDataProduct(user);
            const namespace = () => document.querySelector<HTMLInputElement>('[data-cy="namespace"]');

            await act(() => new Promise((resolve) => setTimeout(resolve, 700)));
            await user.type(await screen.findByRole('textbox', { name: /name/i }), 'sales');

            await waitFor(() => expect(namespace()?.value).toBe('sales'));
            expect(namespace()).toBeDisabled();
        });

        it('should warn before creating a hidden data product', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetTags();
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize();
            mockResourceNamesValidate();
            mockGetDataProductTypes();
            mockDataProductLifecycles();
            mockGetDomains();

            const createHandler = vi.fn(() => HttpResponse.json({ id: 'new-hidden-dp-id' }));
            server.use(http.post('*/api/v2/data_products', createHandler));

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectDataProducts(user);
            await createNewDataProduct(user);
            await fillRequiredDataProductFields(user, {
                name: 'My Hidden Data Product',
                description: 'Secret product details',
                hidden: true,
            });

            await user.click(screen.getByRole('button', { name: 'Create' }));
            await waitFor(() => {
                expect(screen.getAllByRole('button', { name: 'Create' }).length).toBeGreaterThan(1);
            });

            const confirmButtons = screen.getAllByRole('button', { name: 'Create' });
            await user.click(confirmButtons[confirmButtons.length - 1]);

            await waitFor(() => {
                expect(createHandler).toHaveBeenCalled();
            });
        });
    }, 20000);

    describe('Cart should support creating a new exploration', () => {
        it('Should succeed when filling in the form completely', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            // Mock the output ports search (cart items)
            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize();
            mockResourceNamesValidate();
            mockGetDomains();

            const createHandler = vi.fn(() => HttpResponse.json({ id: 'id-1' }));
            server.use(http.post('*/api/v2/explorations', createHandler));

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await createNewExploration(user);

            const nameInput = await screen.findByRole('textbox', { name: /name/i });
            await user.type(nameInput, 'My New exploration');

            const domainSelect = screen.getByRole('combobox', { name: /domain/i });
            await user.click(domainSelect);
            const domainOption = await screen.findByText('Finance');
            await user.click(domainOption);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await user.type(justificationTextArea, 'I need this data for my analysis.');

            const submitButton = await screen.findByRole('button', { name: 'Create' });
            await waitFor(() => expect(submitButton).not.toBeDisabled());
            await user.click(submitButton);

            // Assert the create and link APIs were called
            await waitFor(() => {
                expect(createHandler).toHaveBeenCalled();
            });
        }, 15000);

        it('Should show an error on duplicate namespace', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            // Mock the output ports search (cart items)
            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize();
            mockResourceNamesValidate(ResourceNameValidityType.Duplicate);
            mockGetDomains();

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await createNewExploration(user);

            const nameInput = await screen.findByRole('textbox', { name: /name/i });
            await user.type(nameInput, 'My New exploration');

            // Assert the validation error is shown
            await waitFor(() => {
                expect(screen.getByText('An Exploration with this name already exists')).toBeInTheDocument();
            });
        });
    });

    describe('Cart should reject an exploration name without usable characters', () => {
        it('shows an error and does not create the exploration', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            mockOutputPortsSearch();
            mockUsersHttp(mockUsers);
            mockGetResourceNamesConstraints();
            mockResourceNamesSanitize('');
            mockResourceNamesValidate();
            mockGetDomains();

            const createHandler = vi.fn(() => HttpResponse.json({ id: 'id-1' }));
            server.use(http.post('*/api/v2/explorations', createHandler));

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: ['op-1'] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await createNewExploration(user);
            await user.type(await screen.findByRole('textbox', { name: /name/i }), '!!!');
            await user.click(screen.getByRole('combobox', { name: /domain/i }));
            await user.click(await screen.findByText('Finance'));
            await user.type(
                await screen.findByPlaceholderText('Explain why you need access to these Output Ports'),
                'I need this data for my analysis.',
            );

            const submitButton = await screen.findByRole('button', { name: 'Create' });
            await waitFor(() => expect(submitButton).not.toBeDisabled());
            await user.click(submitButton);

            expect(
                await screen.findByText('The name of the Exploration must contain a letter or a digit'),
            ).toBeInTheDocument();
            expect(createHandler).not.toHaveBeenCalled();
        });
    });

    describe('Cart should support existing explorations', () => {
        it('should allow users to select an existing exploration', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            // Mock the output ports search (cart items)
            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockExplorationsHttp();
            mockExplorationInputPorts(mockExplorations[0].id, []);

            const submitHandler = vi.fn(() => HttpResponse.json({}));
            server.use(http.post(`*/api/v2/explorations/${mockExplorations[0].id}/input_ports`, submitHandler));

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await selectExistingExplorations(user);

            const selectExploration1 = await screen.findByText(mockExplorations[0].name);
            await user.click(selectExploration1);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await waitFor(() => {
                expect(justificationTextArea).toHaveValue(mockExplorations[0].description);
            });

            // Assert that the pre-fill warning is shown
            expect(
                screen.getByText('Pre-filled from the Exploration description. Please review before submitting.'),
            ).toBeInTheDocument();

            // Assert that typing removes the warning
            await user.type(justificationTextArea, ' Extra info.');
            await waitFor(() => {
                expect(
                    screen.queryByText('Pre-filled from the Exploration description. Please review before submitting.'),
                ).toBeNull();
            });

            const submitButton = await screen.findByText('Submit access requests');
            await user.click(submitButton);

            // Assert the submit API was called
            await waitFor(() => {
                expect(submitHandler).toHaveBeenCalled();
            });
        });

        it('When selecting an existing data product with overlap in input ports and the cart it should show a warning', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';

            mockOutputPortsSearch();
            mockExplorationsHttp();
            mockExplorationInputPorts(mockExplorations[0].id);

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await selectExistingExplorations(user);

            const selectExploration1 = await screen.findByText(mockExplorations[0].name);
            await user.click(selectExploration1);

            await waitFor(() => {
                expect(
                    screen.getByText(/Output Ports in the cart, for which the selected Exploration already has access/),
                ).toBeInTheDocument();
            });
        });

        it('should clear stale overlap warnings when switching from existing to new exploration', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';

            mockGetDomains();
            mockOutputPortsSearch();
            mockExplorationsHttp();
            mockExplorationInputPorts(mockExplorations[0].id);

            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await selectExistingExplorations(user);

            const selectExploration1 = await screen.findByText(mockExplorations[0].name);
            await user.click(selectExploration1);

            await waitFor(() => {
                expect(
                    screen.getByText(/Output Ports in the cart, for which the selected Exploration already has access/),
                ).toBeInTheDocument();
            });

            await createNewExploration(user);

            await waitFor(() => {
                expect(
                    screen.queryByText(
                        /Output Ports in the cart, for which the selected Exploration already has access/,
                    ),
                ).toBeNull();
            });
        });
    });

    describe('Cart should persist selection choices across navigation', () => {
        it('should restore the exploration and existing/new selection when navigating away and back', async () => {
            const user = userEvent.setup();
            allowAllAuth();

            const cartOutputPortId = 'op-1';
            mockOutputPortsSearch();
            mockExplorationsHttp();
            mockExplorationInputPorts(mockExplorations[0].id, []);

            const cartWithRoutes = (
                <Routes>
                    <Route
                        path="/cart"
                        element={
                            <>
                                <Cart />
                                <Link to="/other">Go away</Link>
                            </>
                        }
                    />
                    <Route path="/other" element={<Link to="/cart">Back to cart</Link>} />
                </Routes>
            );

            renderWithProviders(cartWithRoutes, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations(user);
            await selectExistingExplorations(user);

            // Navigate away and back
            await user.click(screen.getByText('Go away'));
            await screen.findByText('Back to cart');
            await user.click(screen.getByText('Back to cart'));

            await waitFor(() => {
                expect(screen.getByText('Select an existing Exploration')).toBeInTheDocument();
                expect(screen.getByText('I want to explore this data')).toBeInTheDocument();
            });
        });
    });
});
