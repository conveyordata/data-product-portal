import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { DataProductsTab } from '@/pages/product-studio/components/data-products-tab/data-products-tab.component.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProducts, mockDataProductsHttp } from '@/tests/mocks/data-products.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const preloadedAuthState = {
    auth: { user: mockUsers[0], isLoading: false },
};

function setupMocks(dataProducts = mockDataProducts) {
    allowAllAuth();
    mockDataProductsHttp(dataProducts);
}

describe('DataProductsTab', () => {
    it('shows loading state while fetching', () => {
        allowAllAuth();
        server.use(
            http.get('*/api/v2/data_products', () => {
                return new Promise(() => {
                    //Never resolve promise
                });
            }),
        );
        const { container } = renderWithProviders(<DataProductsTab />, {
            routerProps: { initialEntries: ['/studio'] },
            preloadedState: preloadedAuthState,
        });

        expect(container.querySelector('.ant-spin')).toBeInTheDocument();
    });

    it('displays data products in the table', async () => {
        setupMocks(mockDataProducts);
        renderWithProviders(<DataProductsTab />, {
            routerProps: { initialEntries: ['/studio'] },
            preloadedState: preloadedAuthState,
        });

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });
        expect(screen.getByText('Customer Insights')).toBeInTheDocument();
    });

    it('shows empty state when there are no data products', async () => {
        setupMocks([]);
        renderWithProviders(<DataProductsTab />, {
            routerProps: { initialEntries: ['/studio'] },
            preloadedState: preloadedAuthState,
        });

        await waitFor(() => {
            expect(screen.getByText('Ready to build your first Data Product?')).toBeInTheDocument();
        });
    });

    it('filters data products by search term', async () => {
        setupMocks(mockDataProducts);
        renderWithProviders(<DataProductsTab />, {
            routerProps: { initialEntries: ['/studio'] },
            preloadedState: preloadedAuthState,
        });

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        const searchInput = screen.getByPlaceholderText('Search Data Products by name');
        await userEvent.type(searchInput, 'Customer');

        await waitFor(() => {
            expect(screen.queryByText('Sales Analytics')).not.toBeInTheDocument();
        });
        expect(screen.getByText('Customer Insights')).toBeInTheDocument();
    });

    it('shows no results when search matches nothing', async () => {
        setupMocks(mockDataProducts);
        renderWithProviders(<DataProductsTab />, {
            routerProps: { initialEntries: ['/studio'] },
            preloadedState: preloadedAuthState,
        });

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        const searchInput = screen.getByPlaceholderText('Search Data Products by name');
        await userEvent.type(searchInput, 'nonexistent');

        await waitFor(() => {
            expect(screen.queryByText('Sales Analytics')).not.toBeInTheDocument();
        });
        expect(screen.queryByText('Customer Insights')).not.toBeInTheDocument();
    });

    describe('Create Data Product button', () => {
        it('enables the button when user has create permission', async () => {
            setupMocks(mockDataProducts); // Also gives access on all products
            renderWithProviders(<DataProductsTab />, {
                routerProps: { initialEntries: ['/studio'] },
                preloadedState: preloadedAuthState,
            });

            await waitFor(() => {
                expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
            });

            const button = screen.getByRole('button', { name: 'Create Data Product' });
            expect(button).not.toBeDisabled();
        });

        it('disables the button when user lacks create permission', async () => {
            mockDataProductsHttp(mockDataProducts);
            server.use(
                http.get('*/api/v2/authz/roles/:scope', () => {
                    return HttpResponse.json({ roles: [] });
                }),
                http.get('*/api/v2/authz/access/:action', () => {
                    return HttpResponse.json({ allowed: false });
                }),
                http.get('*/api/v2/authz/role_assignments/:data_product', () => {
                    return HttpResponse.json({ role_assignments: [] });
                }),
            );
            renderWithProviders(<DataProductsTab />, {
                routerProps: { initialEntries: ['/studio'] },
                preloadedState: preloadedAuthState,
            });

            await waitFor(() => {
                expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
            });

            const button = screen.getByRole('button', { name: 'Create Data Product' });
            expect(button).toBeDisabled();
        });
    });
});
