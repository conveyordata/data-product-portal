import { HttpResponse, http } from 'msw';
import { ResourceNameValidityType } from '@/store/api/services/generated/resourceNamesApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockGetResourceNamesConstraints = () => {
    server.use(
        http.get('*/api/v2/resource_names/constraints', () => {
            return HttpResponse.json({ max_length: 64 });
        }),
    );
};

export const mockResourceNamesSanitize = () => {
    server.use(
        http.get('*/api/v2/resource_names/sanitize', ({ request }) => {
            const url = new URL(request.url);
            const name = url.searchParams.get('name');
            return HttpResponse.json({ resource_name: name });
        }),
    );
};

export const mockResourceNamesValidate = () => {
    server.use(
        http.get('*/api/v2/resource_names/validate', () => {
            return HttpResponse.json({ validity: ResourceNameValidityType.Valid });
        }),
    );
};
