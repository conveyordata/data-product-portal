import { HttpResponse, http } from 'msw';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductDetailCalls, mockDataProducts } from '@/tests/mocks/data-products.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, waitFor, within } from '@/tests/test-utils.tsx';

function mockUserCalls() {
    server.use(
        http.get('*/api/v2/users/current', () => {
            return HttpResponse.json(mockUsers[0]);
        }),
        http.get('*/api/v2/users', () => {
            return HttpResponse.json({ users: mockUsers });
        }),
        http.get('*/api/v2/users/current/pending_actions', () => {
            return HttpResponse.json({ pending_actions: [] });
        }),
    );
}

function setupDefaultMocks() {
    allowAllAuth();
    mockDataProductDetailCalls(mockDataProducts[0]);
    mockUserCalls();
    server.use(
        http.get('*/api/v2/configuration/environments', () => {
            return HttpResponse.json({ environment_configs: [] });
        }),
    );
}

function renderDataProductPage(dataProductId = 'dp-1') {
    return renderWithProviders(
        <Routes>
            <Route path="/studio/:dataProductId" element={<DataProduct />} />
        </Routes>,
        {
            routerProps: {
                initialEntries: [`/studio/${dataProductId}`],
            },
            currentUser: mockUsers[0],
        },
    );
}

describe('DataProduct Page', () => {
    it('shows loading spinner while fetching', () => {
        setupDefaultMocks();
        server.use(
            http.get('*/api/v2/data_products/:id', () => {
                return new Promise(() => {
                    //do not resolve promise
                });
            }),
        );
        const { container } = renderDataProductPage();

        expect(container.querySelector('.ant-spin-spinning')).toBeInTheDocument();
    });

    it('renders the data product information', async () => {
        setupDefaultMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });
        expect(screen.getByText('Analytics data product for sales team')).toBeInTheDocument();
        expect(screen.getByText('Draft')).toBeInTheDocument();
        expect(screen.getByText('Sales-domain')).toBeInTheDocument();
        expect(screen.getByText('Reporting')).toBeInTheDocument();
        expect(screen.getByText('analytics-tag')).toBeInTheDocument();
    });

    it('shows edit button when user has edit access', async () => {
        setupDefaultMocks();
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        expect(container.querySelector('[aria-label="edit"]')).toBeInTheDocument();
    });

    it('does not show join team button when user already has access to product', async () => {
        setupDefaultMocks();
        server.use(
            http.get('*/api/v2/authz/role_assignments/data_product', () => {
                return HttpResponse.json({
                    role_assignments: [{ user: { id: '1' }, decision: 'approved' }],
                });
            }),
        );
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        expect(within(container).queryByText('Join Team')).not.toBeInTheDocument();
    });

    it('shows join team button when user does not have access to product', async () => {
        setupDefaultMocks();
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        await waitFor(() => {
            expect(within(container).getByText('Join Team')).toBeInTheDocument();
        });
    });

    it('hides edit button when user lacks edit access', async () => {
        mockDataProductDetailCalls(mockDataProducts[0]);
        mockUserCalls();
        server.use(
            http.get('*/api/v2/authz/roles/:scope', () => {
                return HttpResponse.json({ roles: [] });
            }),
            http.get('*/api/v2/authz/role_assignments/data_product', () => {
                return HttpResponse.json({ role_assignments: [] });
            }),
            http.get('*/api/v2/authz/access/:action', () => {
                return HttpResponse.json({ allowed: false });
            }),
            http.get('*/api/v2/configuration/environments', () => {
                return HttpResponse.json({ environment_configs: [] });
            }),
        );
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        expect(container.querySelector('[aria-label="edit"]')).not.toBeInTheDocument();
    });
});
