import { HttpResponse, http } from 'msw';
import {
    type GetOutputPortAccessTypesApiResponse,
    OutputPortAccessFunction,
    type OutputPortAccessTypesGetItem,
} from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mock_output_port_access_types: OutputPortAccessTypesGetItem[] = [
    OutputPortAccessFunction.Unrestricted,
    OutputPortAccessFunction.Restricted,
    OutputPortAccessFunction.Private,
].map((access_function) => ({
    id: `access-type-${access_function}`,
    name: `${access_function[0].toUpperCase()}${access_function.slice(1)}`,
    description: '',
    access_function,
    output_port_count: 0,
}));

export const mockOutputPortAccessTypes = (
    output_port_access_types: OutputPortAccessTypesGetItem[] = mock_output_port_access_types,
) => {
    server.use(
        http.get('*/api/v2/configuration/output_port_access_types', () => {
            return HttpResponse.json({ output_port_access_types } as GetOutputPortAccessTypesApiResponse);
        }),
    );
};
