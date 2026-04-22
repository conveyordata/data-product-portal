import { HttpResponse, http } from 'msw';
import type {
    DataProductLifeCyclesGetItem,
    GetDataProductsLifecyclesApiResponse,
} from '@/store/api/services/generated/configurationDataProductLifecyclesApi.ts';
import { server } from '@/tests/mocks/server.ts';
export const mock_data_product_lifecycles: DataProductLifeCyclesGetItem[] = [
    {
        id: 'id-1',
        value: 1,
        name: 'Draft',
        color: 'grey',
        is_default: false,
    },
];
export const mockDataProductLifecycles = (
    data_product_lifecycles: DataProductLifeCyclesGetItem[] = mock_data_product_lifecycles,
) => {
    server.use(
        http.get('*/api/v2/configuration/data_product_lifecycles', () => {
            return HttpResponse.json({
                data_product_life_cycles: data_product_lifecycles,
            } as GetDataProductsLifecyclesApiResponse);
        }),
    );
};
