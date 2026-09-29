import { HttpResponse, http } from 'msw';
import {
    type GetOutputPortClassificationsApiResponse,
    OutputPortAccessFunction,
    type OutputPortClassificationsGetItem,
} from '@/store/api/services/generated/configurationOutputPortClassificationsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mock_output_port_classifications: OutputPortClassificationsGetItem[] = [
    OutputPortAccessFunction.Unrestricted,
    OutputPortAccessFunction.Restricted,
    OutputPortAccessFunction.Private,
].map((access_function) => ({
    id: `classification-${access_function}`,
    name: `${access_function[0].toUpperCase()}${access_function.slice(1)}`,
    description: '',
    access_function,
    output_port_count: 0,
}));

export const mockOutputPortClassifications = (
    output_port_classifications: OutputPortClassificationsGetItem[] = mock_output_port_classifications,
) => {
    server.use(
        http.get('*/api/v2/configuration/output_port_classifications', () => {
            return HttpResponse.json({ output_port_classifications } as GetOutputPortClassificationsApiResponse);
        }),
    );
};
