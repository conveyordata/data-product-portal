import { HttpResponse, http } from 'msw';
import {
    OutputPortAccessType,
    OutputPortStatus,
    type SearchOutputPortsResponseItem,
} from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockOutputPorts: SearchOutputPortsResponseItem[] = [
    {
        id: 'op-1',
        namespace: 'op1',
        name: 'op1',
        description: '',
        status: OutputPortStatus.Pending,
        usage: null,
        access_type: OutputPortAccessType.Public,
        data_product_id: 'dp-1',
        tags: [],
        domain: {
            id: 'dom-1',
            name: 'dom1',
            description: 'domain 1',
        },
        lifecycle: null,
        abstract_data_product_count: 1,
        technical_assets_count: 1,
        data_product_name: 'dp-1',
        quality_status: null,
    },
];

export const mockOutputPortsSearch = (output_ports: SearchOutputPortsResponseItem[] = mockOutputPorts) => {
    server.use(
        http.get('*/api/v2/search/output_ports', () => {
            return HttpResponse.json({
                output_ports: output_ports,
            });
        }),
    );
};
