import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import ExplorationsCart from '@/pages/cart-explorations/cart.page.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductOutputPorts } from '@/tests/mocks/dataProductOutputPorts.ts';
import { mockDataProductInputPorts, mockDataProducts, mockDataProductsHttp } from '@/tests/mocks/dataProducts.ts';
import { mockOutputPortsSearch } from '@/tests/mocks/outputPortsSearch.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('Cart', () => {
    const selectDataProducts = async () => {
        const dataProductChoice = await screen.findByText('I want to build Data Products');
        await userEvent.click(dataProductChoice);
    };

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
        server.use(http.post(`*/api/v2/data_products/${mockDataProducts[0].id}/link_input_ports`, submitHandler));

        renderWithProviders(<ExplorationsCart />, {
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

        renderWithProviders(<ExplorationsCart />, {
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
                screen.getByText(/Output Ports in the cart, for which the selected Data Product already has access/),
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

        renderWithProviders(<ExplorationsCart />, {
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
                screen.getByText(/Output Ports, that are part of your selected Data Product, please remove them/),
            ).toBeTruthy();
        });
    });
});
