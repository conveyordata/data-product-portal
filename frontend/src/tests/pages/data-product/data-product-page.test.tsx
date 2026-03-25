import { HttpResponse, http } from 'msw';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductDetailCalls, mockDataProducts } from '@/tests/mocks/data-products.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, waitFor } from '@/tests/test-utils.tsx';

function mockUserCalls() {
    server.use(
        http.get('*/api/v2/users/current', () => {
            return HttpResponse.json(mockUsers[0]);
        }),
        http.get('*/api/v2/users/current/pending_actions', () => {
            return HttpResponse.json({ pending_actions: [] });
        }),
    );
}

function setupMocks() {
    allowAllAuth();
    mockDataProductDetailCalls(mockDataProducts[0]);
    mockUserCalls();
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
        },
    );
}

describe('DataProduct Page', () => {
    it('shows loading spinner while fetching', () => {
        allowAllAuth();
        server.use(
            http.get('*/api/v2/data_products/:id', () => {
                return new Promise(() => {
                    //do not resolve promise
                });
            }),
            http.get('*/api/v2/data_products/dp-1/rolled_up_tags', () => {
                return HttpResponse.json({});
            }),
            http.get('*/api/v2/users/current', () => {
                return HttpResponse.json(mockUsers[0]);
            }),
        );
        const { container } = renderDataProductPage();

        expect(container.querySelector('.ant-spin-spinning')).toBeInTheDocument();
    });

    it('renders the data product information', async () => {
        setupMocks();
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
        setupMocks();
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        // The edit button renders an EditOutlined icon inside a circle button
        expect(container.querySelector('[aria-label="edit"]')).toBeInTheDocument();
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
        );
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        expect(container.querySelector('[aria-label="edit"]')).not.toBeInTheDocument();
    });
});
