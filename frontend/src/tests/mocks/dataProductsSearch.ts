import { HttpResponse, http } from 'msw';
import {
    DataProductIconKey,
    type SearchDataProductsResponseItem,
} from '@/store/api/services/generated/dataProductsSearchApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockDataProducts: SearchDataProductsResponseItem[] = [
    {
        id: 'dp-1',
        name: 'Marketing Campaign Analysis',
        description: 'Campaign KPIs',
        tags: [],
        domain: { id: 'dom-1', name: 'Customer Insights', namespace: 'ci', description: '' },
        type: { id: 'type-1', name: 'Analytics', description: '', icon_key: DataProductIconKey.Analytics },
        lifecycle: null,
        output_ports: [{ id: 'op-1', name: 'Ad Spend vs ROI', description: 'Spend per campaign', access_modes: [] }],
        consumer_count: 2,
    },
];

export const mockDataProductsSearch = (
    dataProducts: SearchDataProductsResponseItem[] = mockDataProducts,
    onRequest: (url: URL) => void = () => undefined,
) => {
    server.use(
        http.get('*/api/v2/search/data_products', ({ request }) => {
            onRequest(new URL(request.url));
            return HttpResponse.json({ data_products: dataProducts });
        }),
    );
};
