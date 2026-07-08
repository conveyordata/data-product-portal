import { HttpResponse, http } from 'msw';
import {
    AbstractDataProductStatus,
    type DataProduct,
    DataProductIconKey,
    DecisionStatus,
    type GetDataProductInputPortsResponse,
    type GetDataProductRolledUpTagsResponse,
    type GetDataProductsResponse,
    type GetDataProductsResponseItem,
    type InputPort,
    OutputPortAccessType,
    OutputPortStatus,
} from '@/store/api/services/generated/dataProductsApi';
import { server } from '@/tests/mocks/server.ts';

export const mockDataProducts: GetDataProductsResponseItem[] = [
    {
        id: 'dp-1',
        name: 'Sales Analytics',
        description: 'Analytics data product for sales team',
        namespace: 'sales namespace',
        status: AbstractDataProductStatus.Active,
        tags: [{ id: 'tag-1', value: 'analytics-tag' }],
        usage: null,
        domain: { id: 'domain-1', name: 'Sales-domain', description: 'Sales domain' },
        type: {
            id: 'type-1',
            name: 'Reporting',
            description: 'Reporting type',
            icon_key: DataProductIconKey.Reporting,
        },
        finalizers: [],
        lifecycle: { id: 'lc-1', name: 'Draft', value: 3, color: 'green', is_default: false },
        user_count: 5,
        input_port_count: 2,
        technical_asset_count: 3,
    },
    {
        id: 'dp-2',
        name: 'Customer Insights',
        finalizers: ['finalizer-1'],
        description: 'Customer behavior and insights',
        namespace: 'marketing',
        status: AbstractDataProductStatus.Active,
        tags: [{ id: 'tag-2', value: 'insights' }],
        usage: null,
        domain: { id: 'domain-2', name: 'Marketing', description: 'Marketing domain' },
        type: {
            id: 'type-2',
            name: 'Exploration',
            description: 'Exploration type',
            icon_key: DataProductIconKey.Exploration,
        },
        lifecycle: { id: 'lc-2', name: 'Production', value: 1, color: 'blue', is_default: true },
        user_count: 3,
        input_port_count: 1,
        technical_asset_count: 2,
    },
];

export const mockDataProductsHttp = (dataProducts: GetDataProductsResponseItem[] = mockDataProducts) => {
    server.use(
        http.get('*/api/v2/data_products', () => {
            return HttpResponse.json({ data_products: dataProducts } satisfies GetDataProductsResponse);
        }),
    );
};

export const mockDataProductHttp = (
    data_product_id: string = mockDataProducts[0].id,
    data_product: DataProduct = mockDataProducts[0],
) => {
    server.use(
        http.get(`*/api/v2/data_products/${data_product_id}`, () => {
            return HttpResponse.json(data_product);
        }),
    );
};

const mockInputPorts: InputPort[] = [
    {
        id: 'id-1',
        justification: 'I need access!',
        output_port_id: 'op-1',
        status: DecisionStatus.Approved,
        is_expiring_soon: false,
        output_port: {
            id: 'op-1',
            name: 'op-1',
            namespace: 'op1',
            description: 'My op1',
            status: OutputPortStatus.Pending,
            access_type: OutputPortAccessType.Public,
            data_product_id: mockDataProducts[1].id,
            tags: [],
        },
    },
];

export const mockDataProductInputPorts = (
    dataProductId: string = mockDataProducts[0].id,
    inputPorts: InputPort[] = mockInputPorts,
) => {
    server.use(
        http.get(`*/api/v2/data_products/${dataProductId}/input_ports`, () => {
            return HttpResponse.json({ input_ports: inputPorts } satisfies GetDataProductInputPortsResponse);
        }),
    );
};

export const mockDataProductDetailCalls = (dataProduct: GetDataProductsResponseItem) => {
    mockDataProductHttp(dataProduct.id, dataProduct);
    server.use(
        http.get(`*/api/v2/data_products/${dataProduct.id}/rolled_up_tags`, () => {
            return HttpResponse.json({ rolled_up_tags: [] } satisfies GetDataProductRolledUpTagsResponse);
        }),
        http.get(`*/api/v2/data_products/${dataProduct.id}/role_assignments`, () => {
            return HttpResponse.json({ role_assignments: [] });
        }),
        http.get(`*/api/v2/data_products/${dataProduct.id}/history`, () => {
            return HttpResponse.json({ events: [] });
        }),
        http.get(`*/api/v2/data_products/${dataProduct.id}/settings`, () => {
            return HttpResponse.json({ data_product_settings: [] });
        }),
        http.get('*/api/v2/plugins/platform-tiles', () => {
            return HttpResponse.json({});
        }),
    );
};
