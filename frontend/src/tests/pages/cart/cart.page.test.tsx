import { HttpResponse, http } from 'msw';
import { Link, Route, Routes } from 'react-router';
import { afterEach, describe, expect, it, vi } from 'vitest';
import Cart from '@/pages/cart/cart.page.tsx';
import { ResourceNameValidityType } from '@/store/api/services/generated/resourceNamesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductLifecycles } from '@/tests/mocks/configurationDataProductLifecycles.ts';
import { mockGetDataProductTypes } from '@/tests/mocks/configurationDataProductTypes.ts';
import { mockGetDomains } from '@/tests/mocks/configurationDomains.ts';
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
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

afterEach(() => {
    localStorage.clear();
});

describe('Cart', () => {
    const selectDataProducts = async () => {
        const dataProductChoice = await screen.findByText('I want to build Data Products');
        await userEvent.click(dataProductChoice);
    };
    const selectExplorations = async () => {
        const explorationsChoice = await screen.findByText('I want to explore this data');
        await userEvent.click(explorationsChoice);
    };
    const selectExistingExplorations = async () => {
        const existingChoice = await screen.findByText('Select an existing Exploration');
        await userEvent.click(existingChoice);
    };
    describe('Empty cart page', () => {
        it('Should show a message to direct to the Marketplace', async () => {
            renderWithProviders(<Cart />, {
                routerProps: { initialEntries: ['/cart'] },
                currentUser: mockUsers[0],
            });

            await screen.findByText(/Your cart is currently empty/);
        });
    });
    describe('Cart should support existing data products', () => {
        const selectExistingDataProducts = async () => {
            const existingChoice = await screen.findByText('Select an existing Data Product');
            await userEvent.click(existingChoice);
        };
        it('should allow users to select an existing data product', async () => {
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

            await selectDataProducts();
            await selectExistingDataProducts();

            const selectDataProduct1 = await screen.findByText(mockDataProducts[0].name);
            await userEvent.click(selectDataProduct1);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await userEvent.type(justificationTextArea, 'I need this data for my analysis.');

            const submitButton = await screen.findByText('Submit access requests');
            await userEvent.click(submitButton);

            // Assert the submit API was called
            await waitFor(() => {
                expect(submitHandler).toHaveBeenCalled();
            });
        });

        it('When selecting an existing data product with overlap in input ports and the cart it should show a warning', async () => {
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

            await selectDataProducts();
            await selectExistingDataProducts();

            const selectDataProduct1 = await screen.findByText(mockDataProducts[0].name);
            await userEvent.click(selectDataProduct1);

            await waitFor(() => {
                expect(
                    screen.getByText(
                        /Output Ports in the cart, for which the selected Data Product already has access/,
                    ),
                ).toBeTruthy();
            });
        });

        it('When selecting an existing data product with overlap in output ports and the cart should show a warning', async () => {
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

            await selectDataProducts();
            await selectExistingDataProducts();

            const selectDataProduct1 = await screen.findByText(mockDataProducts[0].name);
            await userEvent.click(selectDataProduct1);

            await waitFor(() => {
                expect(screen.getByText(/Output Ports, that are part of your selected Data Product/)).toBeTruthy();
            });
        });
    });

    describe('Cart should support creating a new data product', () => {
        const createNewDataProduct = async () => {
            const existingChoice = await screen.findByText('Create a new Data Product');
            await userEvent.click(existingChoice);
        };
        it('Should succeed when filling in the form completely', async () => {
            allowAllAuth();

            // Mock the output ports search (cart items)
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

            await selectDataProducts();
            await createNewDataProduct();

            const nameInput = await screen.findByRole('textbox', { name: /name/i });
            await userEvent.type(nameInput, 'My New Data Product');

            const typeSelect = screen.getByRole('combobox', { name: /type/i });
            await userEvent.click(typeSelect);
            const typeOption = await screen.findByText('Reporting');
            await userEvent.click(typeOption);

            const statusSelect = screen.getByRole('combobox', { name: /status/i });
            await userEvent.click(statusSelect);
            const statusOption = await screen.findByText('Draft');
            await userEvent.click(statusOption);

            const domainSelect = screen.getByRole('combobox', { name: /domain/i });
            await userEvent.click(domainSelect);
            const domainOption = await screen.findByText('Finance');
            await userEvent.click(domainOption);

            const descriptionTextArea = screen.getByRole('textbox', { name: /description/i });
            await userEvent.type(descriptionTextArea, 'A detailed description of the data product.');

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await userEvent.type(justificationTextArea, 'I need this data for my analysis.');

            const submitButton = await screen.findByText('Create');
            await userEvent.click(submitButton);

            // Assert the create and link APIs were called
            await waitFor(() => {
                expect(createHandler).toHaveBeenCalled();
            });
        });
    }, 20000);

    describe('Cart should support creating a new exploration', () => {
        const createNewExploration = async () => {
            const existingChoice = await screen.findByText('Create a new Exploration');
            await userEvent.click(existingChoice);
        };

        it('Should succeed when filling in the form completely', async () => {
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

            await selectExplorations();
            await createNewExploration();

            const nameInput = await screen.findByRole('textbox', { name: /name/i });
            await userEvent.type(nameInput, 'My New exploration');

            const domainSelect = screen.getByRole('combobox', { name: /domain/i });
            await userEvent.click(domainSelect);
            const domainOption = await screen.findByText('Finance');
            await userEvent.click(domainOption);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await userEvent.type(justificationTextArea, 'I need this data for my analysis.');

            const submitButton = await screen.findByRole('button', { name: 'Create' });
            await waitFor(() => expect(submitButton).not.toBeDisabled());
            await userEvent.click(submitButton);

            // Assert the create and link APIs were called
            await waitFor(() => {
                expect(createHandler).toHaveBeenCalled();
            });
        }, 15000);

        it('Should show an error on duplicate namespace', async () => {
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

            await selectExplorations();
            await createNewExploration();

            const nameInput = await screen.findByRole('textbox', { name: /name/i });
            await userEvent.type(nameInput, 'My New exploration');

            // Assert the validation error is shown
            await waitFor(() => {
                expect(screen.getByText('An Exploration with this name already exists')).toBeTruthy();
            });
        });
    });

    describe('Cart should support existing explorations', () => {
        it('should allow users to select an existing exploration', async () => {
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

            await selectExplorations();
            await selectExistingExplorations();

            const selectExploration1 = await screen.findByText(mockExplorations[0].name);
            await userEvent.click(selectExploration1);

            const justificationTextArea = await screen.findByPlaceholderText(
                'Explain why you need access to these Output Ports',
            );
            await waitFor(() => {
                expect(justificationTextArea).toHaveValue(mockExplorations[0].description);
            });

            // Assert that the pre-fill warning is shown
            expect(
                screen.getByText('Pre-filled from the Exploration description. Please review before submitting.'),
            ).toBeTruthy();

            // Assert that typing removes the warning
            await userEvent.type(justificationTextArea, ' Extra info.');
            await waitFor(() => {
                expect(
                    screen.queryByText('Pre-filled from the Exploration description. Please review before submitting.'),
                ).toBeNull();
            });

            const submitButton = await screen.findByText('Submit access requests');
            await userEvent.click(submitButton);

            // Assert the submit API was called
            await waitFor(() => {
                expect(submitHandler).toHaveBeenCalled();
            });
        });

        it('When selecting an existing data product with overlap in input ports and the cart it should show a warning', async () => {
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

            await selectExplorations();
            await selectExistingExplorations();

            const selectExploration1 = await screen.findByText(mockExplorations[0].name);
            await userEvent.click(selectExploration1);

            await waitFor(() => {
                expect(
                    screen.getByText(/Output Ports in the cart, for which the selected Exploration already has access/),
                ).toBeTruthy();
            });
        });
    });

    describe('Cart should persist selection choices across navigation', () => {
        it('should restore the exploration and existing/new selection when navigating away and back', async () => {
            allowAllAuth();

            const cartOutputPortId = 'op-1';
            mockOutputPortsSearch();
            mockExplorationsHttp();
            mockExplorationInputPorts(mockExplorations[0].id, []);

            const CartWithRoutes = () => (
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

            renderWithProviders(<CartWithRoutes />, {
                routerProps: { initialEntries: ['/cart'] },
                preloadedState: { cart: { DatasetIds: [cartOutputPortId] } },
                currentUser: mockUsers[0],
            });

            await selectExplorations();
            await selectExistingExplorations();

            // Navigate away and back
            await userEvent.click(screen.getByText('Go away'));
            await screen.findByText('Back to cart');
            await userEvent.click(screen.getByText('Back to cart'));

            await waitFor(() => {
                expect(screen.getByText('Select an existing Exploration')).toBeTruthy();
                expect(screen.getByText('I want to explore this data')).toBeTruthy();
            });
        });
    });
});
