import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { OutputPortCard } from '@/components/output-ports/output-port-card/output-port-card.component.tsx';
import {
    AccessDurationType,
    type GetOutputPortResponse,
    OutputPortAccessType,
    OutputPortStatus,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    AbstractDataProductStatus,
    DataProductIconKey,
    type GetTechnicalAssetsResponseItem,
    TechnicalAssetStatus,
    TechnicalMapping,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL } from '@/store/common/api-errors.ts';
import { server } from '@/tests/mocks/server.ts';
import { fireEvent, renderWithProviders, screen, waitFor, within } from '@/tests/test-utils.tsx';

const dataset: GetOutputPortResponse = {
    id: 'op-1',
    namespace: 'sales.orders',
    name: 'Orders output port',
    description: 'Orders dataset',
    status: OutputPortStatus.Active,
    usage: null,
    access_type: OutputPortAccessType.Public,
    data_product_access_duration_type: AccessDurationType.Permanent,
    exploration_access_duration_type: AccessDurationType.Permanent,
    data_product_id: 'dp-1',
    tags: [],
    domain: {
        id: 'domain-1',
        name: 'Sales',
        description: 'Sales domain',
    },
    lifecycle: null,
    access_modes: [],
    about: null,
    rolled_up_tags: [],
    data_product_settings: [],
    technical_asset_links: [],
};

const technicalAsset: GetTechnicalAssetsResponseItem = {
    id: 'ta-1',
    name: 'Orders asset',
    description: 'Orders technical asset',
    namespace: 'sales.orders.asset',
    owner_id: 'dp-1',
    platform_id: 'platform-1',
    service_id: 'service-1',
    status: TechnicalAssetStatus.Active,
    technical_mapping: TechnicalMapping.Default,
    access_modes: [
        {
            id: 'write',
            name: 'Write',
            description: 'Write access',
        },
    ],
    configuration: {
        configuration_type: 'S3TechnicalAssetConfiguration',
        bucket: 'bucket',
        path: '/orders',
    },
    owner: {
        id: 'dp-1',
        name: 'Sales data product',
        namespace: 'sales',
        description: 'Sales',
        status: AbstractDataProductStatus.Active,
        type: {
            id: 'type-1',
            name: 'Source',
            description: 'Source',
            icon_key: DataProductIconKey.Default,
        },
    },
    output_port_links: [],
    tags: [],
    sourceAligned: false,
    result_string: 's3://bucket/orders',
    technical_info: [],
};

describe('OutputPortCard', () => {
    it('opens the incompatible access modes modal when linking fails with incompatible modes', async () => {
        server.use(
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId', () =>
                HttpResponse.json({
                    ...dataset,
                    access_modes: [
                        {
                            id: 'read',
                            name: 'Read',
                            description: 'Read access',
                        },
                    ],
                }),
            ),
            http.get('*/api/v2/data_products/:dataProductId/technical_assets/:technicalAssetId', () =>
                HttpResponse.json(technicalAsset),
            ),
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
            http.post('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId/technical_assets/add', () =>
                HttpResponse.json({ detail: INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL }, { status: 400 }),
            ),
        );

        renderWithProviders(<OutputPortCard outputPortId={dataset.id} dataProductId={dataset.data_product_id} />, {
            routerProps: { initialEntries: ['/'] },
        });

        const card = await screen.findByText(dataset.name);

        fireEvent.drop(card.closest('.ant-card') as HTMLElement, {
            dataTransfer: {
                getData: () => JSON.stringify({ type: 'data-output', id: 'ta-1', name: 'Orders asset' }),
            },
        });

        await waitFor(() => {
            expect(screen.getByText('Incompatible access modes')).toBeInTheDocument();
        });
        const modal = screen.getByRole('dialog');
        await waitFor(() => {
            expect(within(modal).getByText(/Orders output port/i)).toBeInTheDocument();
            expect(within(modal).getByText(/Orders asset/i)).toBeInTheDocument();
        });
    });
});
