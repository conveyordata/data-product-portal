import { HttpResponse, http } from 'msw';
import {
    DataProductStatus,
    DecisionStatus,
    type Exploration,
    type GetExplorationInputPortsResponse,
    type GetExplorationsResponse,
    type InputPort,
    OutputPortAccessType,
    OutputPortStatus,
} from '@/store/api/services/generated/explorationsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockExplorations: Exploration[] = [
    {
        id: 'exp-1',
        name: 'CEO Question',
        description: 'Want to answer questions from the CEO',
        namespace: 'sales namespace',
        domain: { id: 'domain-1', name: 'Sales-domain', description: 'Sales domain' },
        finalizers: ['finalizer-1', 'finalizer-2'],
        status: DataProductStatus.Active,
    },
    {
        id: 'exp-2',
        name: 'COO Question',
        description: 'Want to answer questions from the COO',
        namespace: 'marketing',
        domain: { id: 'domain-2', name: 'Marketing', description: 'Marketing domain' },
        finalizers: [],
        status: DataProductStatus.Active,
    },
];

export const mockExplorationsHttp = (explorations: Exploration[] = mockExplorations) => {
    server.use(
        http.get('*/api/v2/explorations', () => {
            return HttpResponse.json({ explorations: explorations } satisfies GetExplorationsResponse);
        }),
    );
};

const mockInputPorts: InputPort[] = [
    {
        id: 'id-1',
        justification: 'I am your king!',
        status: DecisionStatus.Approved,
        output_port_id: 'op-1',
        output_port: {
            id: 'op-1',
            name: 'Output port numero uno',
            namespace: 'op_numero_uno',
            description: 'I am the first output port',
            status: OutputPortStatus.Pending,
            access_type: OutputPortAccessType.Public,
            data_product_id: 'dp-1',
            tags: [],
        },
    },
];

export const mockExplorationInputPorts = (
    dataProductId: string = mockExplorations[0].id,
    inputPorts: InputPort[] = mockInputPorts,
) => {
    server.use(
        http.get(`*/api/v2/explorations/${dataProductId}/input_ports`, () => {
            return HttpResponse.json({ input_ports: inputPorts } satisfies GetExplorationInputPortsResponse);
        }),
    );
};
