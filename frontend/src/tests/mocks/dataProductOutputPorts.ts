import { HttpResponse, http } from 'msw';
import {
    type GetDataProductOutputPortsResponse,
    type OutputPort,
    OutputPortAccessType,
    OutputPortStatus,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { server } from '@/tests/mocks/server.ts';

const mockOutputPorts: OutputPort[] = [
    {
        id: 'op-1',
        name: 'op1',
        namespace: 'op1',
        description: 'Output port 1',
        status: OutputPortStatus.Pending,
        access_type: OutputPortAccessType.Public,
        data_product_id: 'dp-1',
        tags: [],
    },
];

export const mockDataProductOutputPorts = (
    dataProductId: string = mockOutputPorts[0].id,
    outputPorts: OutputPort[] = mockOutputPorts,
) => {
    server.use(
        http.get(`*/api/v2/data_products/${dataProductId}/output_ports`, () => {
            return HttpResponse.json({ output_ports: outputPorts } satisfies GetDataProductOutputPortsResponse);
        }),
    );
};
