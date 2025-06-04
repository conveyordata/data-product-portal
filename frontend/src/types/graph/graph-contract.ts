import { CustomNodeTypes } from '@/components/charts/node-editor/node-types';

import { DataProductRoleAssignmentContract } from '../roles/role.contract';

export interface NodeContract {
    id: string;
    data: {
        id: string;
        name: string;
        icon_key: string | undefined;
        link_to_id: string | undefined;
        domain: string | undefined;
        domain_id: string | undefined;
        assignments: Array<DataProductRoleAssignmentContract> | undefined;
        description: string | undefined;
    };
    isMain: boolean;
    type: CustomNodeTypes;
}

export interface EdgeContract {
    id: string;
    source: string;
    target: string;
    animated: boolean;
}

export interface GraphContract {
    nodes: NodeContract[];
    edges: EdgeContract[];
}
