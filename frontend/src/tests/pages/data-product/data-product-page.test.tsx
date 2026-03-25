import { HttpResponse, http } from 'msw';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProductDetail, mockDataProductDetailHttp } from '@/tests/mocks/data-products.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, waitFor } from '@/tests/test-utils.tsx';

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

function setupMocks() {
    allowAllAuth();
    mockDataProductDetailHttp(mockDataProductDetail);
    server.use(
        http.get('*/api/v2/users/current', () => {
            return HttpResponse.json(mockCurrentUser);
        }),
        http.get('*/api/v2/users/current/pending_actions', () => {
            return HttpResponse.json({ pending_actions: [] });
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
        },
    );
}

describe('DataProduct Page', () => {
    it('shows loading spinner while fetching', () => {
        allowAllAuth();
        server.use(
            http.get('*/api/v2/data_products/:id', () => {
                return new Promise(() => {});
            }),
            http.get('*/api/v2/data_products/:id/rolled_up_tags', () => {
                return new Promise(() => {});
            }),
            http.get('*/api/v2/users/current', () => {
                return HttpResponse.json(mockCurrentUser);
            }),
            http.get('*/api/v2/users/current/pending_actions', () => {
                return HttpResponse.json({ pending_actions: [] });
            }),
        );
        const { container } = renderDataProductPage();

        expect(container.querySelector('.ant-spin-spinning')).toBeInTheDocument();
    });

    it('renders the data product name', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });
    });

    it('renders the data product description', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Analytics data product for sales team')).toBeInTheDocument();
        });
    });

    it('displays lifecycle status', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Production')).toBeInTheDocument();
        });
    });

    it('displays domain name', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales')).toBeInTheDocument();
        });
    });

    it('displays data product type', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Reporting')).toBeInTheDocument();
        });
    });

    it('displays tags', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('analytics')).toBeInTheDocument();
        });
    });

    it('displays namespace', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('sales')).toBeInTheDocument();
        });
    });

    it('shows tabs for the data product', async () => {
        setupMocks();
        renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('About')).toBeInTheDocument();
        });
        expect(screen.getByText('Input Ports')).toBeInTheDocument();
        expect(screen.getByText('Output Ports')).toBeInTheDocument();
        expect(screen.getByText('Team')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
        expect(screen.getByText('History')).toBeInTheDocument();
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
        server.use(
            http.get('*/api/v2/authz/roles/:scope', () => {
                return HttpResponse.json({ roles: [] });
            }),
            http.get('*/api/v2/authz/access/:action', () => {
                return HttpResponse.json({ allowed: false });
            }),
            http.get('*/api/v2/users/current', () => {
                return HttpResponse.json(mockCurrentUser);
            }),
            http.get('*/api/v2/users/current/pending_actions', () => {
                return HttpResponse.json({ pending_actions: [] });
            }),
        );
        mockDataProductDetailHttp(mockDataProductDetail);
        const { container } = renderDataProductPage();

        await waitFor(() => {
            expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
        });

        expect(container.querySelector('[aria-label="edit"]')).not.toBeInTheDocument();
    });
});
