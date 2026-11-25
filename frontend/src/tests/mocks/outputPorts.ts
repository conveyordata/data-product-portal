import { HttpResponse, http } from 'msw';
import {
    AccessDurationType,
    type GetOutputPortsResponseItem,
    OutputPortAccessFunction,
    OutputPortStatus,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockOutputPorts: GetOutputPortsResponseItem[] = [
    {
        id: 'op-1',
        namespace: 'op1',
        name: 'op1',
        description: '',
        status: OutputPortStatus.Pending,
        usage: null,
        access_type: {
            id: 'access-type-1',
            name: 'Unrestricted',
            access_function: OutputPortAccessFunction.Unrestricted,
        },
        data_product_id: 'dp-1',
        tags: [],
        domain: {
            id: 'dom-1',
            name: 'dom1',
            namespace: 'dom1',
            description: 'domain 1',
        },
        lifecycle: null,
        abstract_data_product_count: 1,
        technical_assets_count: 1,
        data_product_name: 'dp-1',
        access_modes: [],
        data_product_access_duration_type: AccessDurationType.Permanent,
        exploration_access_duration_type: AccessDurationType.Permanent,
    },
];

export const mockGetOutputPorts = (output_ports: GetOutputPortsResponseItem[] = mockOutputPorts) => {
    server.use(
        http.get('*/api/v2/output_ports', () => {
            return HttpResponse.json({
                output_ports: output_ports,
            });
        }),
    );
};
