import { HttpResponse, http } from 'msw';
import { server } from '@/tests/mocks/server.ts';

export const mockCreateTechnicalAsset = (data_product_id: string) => {
    server.use(
        http.post(`*/api/v2/data_products/${data_product_id}/technical_assets`, () => {
            return HttpResponse.json({ id: '1' });
        }),
    );
};
