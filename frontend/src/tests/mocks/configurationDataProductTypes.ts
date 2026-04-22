import { HttpResponse, http } from 'msw';
import {
    DataProductIconKey,
    type DataProductTypesGet,
    type DataProductTypesGetItem,
} from '@/store/api/services/generated/configurationDataProductTypesApi.ts';
import { server } from '@/tests/mocks/server.ts';
export const mock_data_product_types: DataProductTypesGetItem[] = [
    {
        id: 'type-1',
        name: 'Reporting',
        description: 'Reporting type',
        icon_key: DataProductIconKey.Reporting,
        data_product_count: 0,
    },
];
export const mockGetDataProductTypes = (data_product_types: DataProductTypesGetItem[] = mock_data_product_types) => {
    server.use(
        http.get('*/api/v2/configuration/data_product_types', () => {
            return HttpResponse.json({ data_product_types: data_product_types } as DataProductTypesGet);
        }),
    );
};
