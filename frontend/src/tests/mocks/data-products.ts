import { HttpResponse, http } from 'msw';
import {
    DataProductIconKey,
    DataProductStatus,
    type GetDataProductRolledUpTagsResponse,
    type GetDataProductsResponse,
    type GetDataProductsResponseItem,
} from '@/store/api/services/generated/dataProductsApi';
import { server } from '@/tests/mocks/server.ts';

export const mockDataProducts: GetDataProductsResponseItem[] = [
    {
        id: 'dp-1',
        name: 'Sales Analytics',
        description: 'Analytics data product for sales team',
        namespace: 'sales namespace',
        status: DataProductStatus.Active,
        tags: [{ id: 'tag-1', value: 'analytics-tag' }],
        usage: null,
        domain: { id: 'domain-1', name: 'Sales-domain', description: 'Sales domain' },
        type: {
            id: 'type-1',
            name: 'Reporting',
            description: 'Reporting type',
            icon_key: DataProductIconKey.Reporting,
        },
        lifecycle: { id: 'lc-1', name: 'Draft', value: 3, color: 'green', is_default: false },
        user_count: 5,
        output_port_count: 2,
        technical_asset_count: 3,
    },
    {
        id: 'dp-2',
        name: 'Customer Insights',
        description: 'Customer behavior and insights',
        namespace: 'marketing',
        status: DataProductStatus.Active,
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
        output_port_count: 1,
        technical_asset_count: 2,
    },
];

export const mockDataProductsHttp = (dataProducts: GetDataProductsResponseItem[]) => {
    server.use(
        http.get('*/api/v2/data_products', () => {
            return HttpResponse.json({ data_products: dataProducts } satisfies GetDataProductsResponse);
        }),
    );
};

export const mockDataProductDetailCalls = (dataProduct: GetDataProductsResponseItem) => {
    server.use(
        http.get(`*/api/v2/data_products/${dataProduct.id}`, () => {
            return HttpResponse.json({
                ...dataProduct,
            });
        }),
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
