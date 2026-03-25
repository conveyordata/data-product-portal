import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { DataProductsTab } from '@/pages/product-studio/components/data-products-tab/data-products-tab.component.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProducts, mockDataProductsHttp } from '@/tests/mocks/data-products.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const mockCurrentUser = {
    id: 'user-1',
    email: 'alice@example.com',
    external_id: 'ext-1',
    first_name: 'Alice',
    last_name: 'Smith',
    has_seen_tour: true,
    can_become_admin: false,
    global_role: null,
};

const preloadedAuthState = {
    auth: { user: mockCurrentUser, isLoading: false },
};

function setupMocks(dataProducts = mockDataProducts) {
    allowAllAuth();
    mockDataProductsHttp(dataProducts);
}

function renderTab(dataProducts = mockDataProducts) {
    setupMocks(dataProducts);
    return renderWithProviders(<DataProductsTab />, {
        routerProps: { initialEntries: ['/studio'] },
        preloadedState: preloadedAuthState,
    });
}

describe('DataProductsTab', () => {
    it('shows loading state while fetching', () => {
        allowAllAuth();
        server.use(
            http.get('*/api/v2/data_products', () => {
                return new Promise(() => {});
            }),
        );
        const { container } = renderWithProviders(<DataProductsTab />, {
            routerProps: { initialEntries: ['/studio'] },
            preloadedState: preloadedAuthState,
        });

        expect(container.querySelector('.ant-spin')).toBeInTheDocument();
    });

    it('displays data products in the table', async () => {
        renderTab();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });
        expect(screen.getByText('Customer Insights')).toBeInTheDocument();
    });

    it('shows empty state when there are no data products', async () => {
        renderTab([]);

        await waitFor(() => {
            expect(screen.getByText('Ready to build your first Data Product?')).toBeInTheDocument();
        });
    });

    it('filters data products by search term', async () => {
        renderTab();

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
        renderTab();

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
        it('renders the Create Data Product button when data products exist', async () => {
            renderTab();

            await waitFor(() => {
                expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
            });

            expect(screen.getByRole('button', { name: 'Create Data Product' })).toBeInTheDocument();
        });

        it('renders the Create Data Product button in empty state', async () => {
            renderTab([]);

            await waitFor(() => {
                expect(screen.getByText('Ready to build your first Data Product?')).toBeInTheDocument();
            });

            expect(screen.getByRole('button', { name: 'Create Data Product' })).toBeInTheDocument();
        });

        it('enables the button when user has create permission', async () => {
            renderTab();

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

        it('links to the create data product page', async () => {
            renderTab();

            await waitFor(() => {
                expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
            });

            const link = screen.getByRole('link', { name: 'Create Data Product' });
            expect(link).toHaveAttribute('href', '/studio/new');
        });
    });
});
