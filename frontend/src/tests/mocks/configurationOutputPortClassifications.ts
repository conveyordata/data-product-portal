import { HttpResponse, http } from 'msw';
import {
    type GetOutputPortClassificationsApiResponse,
    OutputPortAccessType,
    type OutputPortClassificationsGetItem,
} from '@/store/api/services/generated/configurationOutputPortClassificationsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mock_output_port_classifications: OutputPortClassificationsGetItem[] = [
    OutputPortAccessType.Unrestricted,
    OutputPortAccessType.Restricted,
    OutputPortAccessType.Private,
].map((access_type) => ({
    id: `classification-${access_type}`,
    name: `${access_type[0].toUpperCase()}${access_type.slice(1)}`,
    description: '',
    access_type,
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
