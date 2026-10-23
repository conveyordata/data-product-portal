import { delay, HttpResponse, http } from 'msw';
import {
    ResourceNameValidityType,
    type ValidateResourceNameApiResponse,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockGetResourceNamesConstraints = () => {
    server.use(
        http.get('*/api/v2/resource_names/constraints', () => {
            return HttpResponse.json({ max_length: 64 });
        }),
    );
};

export const mockResourceNamesSanitize = (resourceName?: string, latencyMs = 0) => {
    server.use(
        http.get('*/api/v2/resource_names/sanitize', async ({ request }) => {
            await delay(latencyMs);
            const url = new URL(request.url);
            const name = url.searchParams.get('name');
            return HttpResponse.json({ resource_name: resourceName ?? name });
        }),
    );
};

export const mockResourceNamesValidate = (validity: ResourceNameValidityType = ResourceNameValidityType.Valid) => {
    server.use(
        http.get('*/api/v2/resource_names/validate', () => {
            return HttpResponse.json({ validity } as ValidateResourceNameApiResponse);
        }),
    );
};
