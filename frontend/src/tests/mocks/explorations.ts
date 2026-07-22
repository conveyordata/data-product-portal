import { HttpResponse, http } from 'msw';
import {
    AbstractDataProductStatus,
    DecisionStatus,
    type Exploration,
    type GetExplorationInputPortsResponse,
    type GetExplorationsResponse,
    type AbstractDataProductInputPort as InputPort,
    InputPortStatus,
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
        status: AbstractDataProductStatus.Active,
    },
    {
        id: 'exp-2',
        name: 'COO Question',
        description: 'Want to answer questions from the COO',
        namespace: 'marketing',
        domain: { id: 'domain-2', name: 'Marketing', description: 'Marketing domain' },
        finalizers: [],
        status: AbstractDataProductStatus.Active,
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
        status: InputPortStatus.Approved,
        output_port_id: 'op-1',
        current_request: {
            id: 'request-1',
            justification: 'I am your king!',
            valid_until: null,
            decision: DecisionStatus.Approved,
            created_on: '2024-03-15T10:00:00Z',
            requested_on: '2024-03-15T10:00:00Z',
            requested_by: {
                id: 'user-1',
                email: 'alice@example.com',
                external_id: 'ext-1',
                first_name: 'Alice',
                last_name: 'Smith',
                has_seen_tour: true,
                can_become_admin: false,
            },
        },
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
