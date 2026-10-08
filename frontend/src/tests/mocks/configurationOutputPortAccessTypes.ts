import { HttpResponse, http } from 'msw';
import type { GetOutputPortAccessTypesApiResponse } from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { ACCESS_FUNCTION_ORDER } from '@/utils/access-function.helper.tsx';

const output_port_access_types = ACCESS_FUNCTION_ORDER.map((access_function) => ({
    id: `access-type-${access_function}`,
    name: `${access_function[0].toUpperCase()}${access_function.slice(1)}`,
    description: '',
    access_function,
    output_port_count: 0,
}));

export const mockOutputPortAccessTypes = () => {
    server.use(
        http.get('*/api/v2/configuration/output_port_access_types', () => {
            return HttpResponse.json({ output_port_access_types } as GetOutputPortAccessTypesApiResponse);
        }),
    );
};
