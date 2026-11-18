import { HttpResponse, http } from 'msw';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { TechnicalAsset } from '@/pages/technical-asset/technical-asset.page.tsx';
import {
    type GetTechnicalAssetResponse,
    TechnicalAssetStatus,
    TechnicalMapping,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { mockDataProductDetailCalls, mockDataProducts } from '@/tests/mocks/dataProducts.ts';
import { mockGetPlugins } from '@/tests/mocks/plugins.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';

const dataProduct = mockDataProducts[0];

const technicalAsset = {
    id: 'ta-1',
    name: 'Sales Bucket',
    description: 'Raw sales files',
    namespace: 'sales-bucket',
    owner_id: dataProduct.id,
    status: TechnicalAssetStatus.Active,
    technical_mapping: TechnicalMapping.Default,
    access_modes: [],
    configuration: { name: 'S3TechnicalAssetConfiguration' },
    owner: dataProduct,
    environments: [],
    output_port_links: [],
    tags: [],
    environment_values: {},
    sourceAligned: false,
    result_string: '',
    technical_info: [],
} as GetTechnicalAssetResponse;

function setupMocks(allowedAction: AuthorizationAction) {
    mockDataProductDetailCalls();
    mockGetPlugins();
    server.use(
        http.get(`*/api/v2/data_products/${dataProduct.id}/technical_assets/${technicalAsset.id}`, () =>
            HttpResponse.json(technicalAsset),
        ),
        http.get(`*/api/v2/data_products/${dataProduct.id}/technical_assets/${technicalAsset.id}/history`, () =>
            HttpResponse.json({ events: [] }),
        ),
        http.get('*/api/v2/authz/role_assignments/:scope', () => HttpResponse.json({ role_assignments: [] })),
        http.get('*/api/v2/authz/access/:action', ({ params }) =>
            HttpResponse.json({ allowed: Number(params.action) === allowedAction }),
        ),
    );
}

function renderTechnicalAssetPage() {
    return renderWithProviders(
        <Routes>
            <Route path="/studio/:dataProductId/:dataOutputId" element={<TechnicalAsset />} />
        </Routes>,
        {
            routerProps: { initialEntries: [`/studio/${dataProduct.id}/${technicalAsset.id}`] },
            currentUser: mockUsers[0],
        },
    );
}

describe('TechnicalAsset Page', () => {
    it('shows the edit button to users who may update technical assets', async () => {
        setupMocks(AuthorizationAction.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET);
        renderTechnicalAssetPage();

        expect(await screen.findByLabelText('edit')).toBeInTheDocument();
    });
});
