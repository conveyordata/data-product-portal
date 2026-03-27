import { HttpResponse, http } from 'msw';
import {
    type DataProduct,
    DataProductIconKey,
    DataProductStatus,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mock_data_products: DataProduct[] = [
    {
        id: '1',
        name: 'product 1',
        namespace: '',
        description: '',
        status: DataProductStatus.Pending,
        type: {
            id: '1',
            name: 'reporting',
            description: 'I am a reporting type',
            icon_key: DataProductIconKey.Reporting,
        },
    },
];

export const mockDataProductHttp = (
    data_product_id: string = mock_data_products[0].id,
    data_product: DataProduct = mock_data_products[0],
) => {
    server.use(
        http.get(`*/api/v2/data_products/${data_product_id}`, () => {
            return HttpResponse.json(data_product);
        }),
    );
};
