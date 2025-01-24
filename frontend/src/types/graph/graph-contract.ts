import { CustomNodeTypes } from '@/components/charts/node-editor/node-types';

export interface NodeContract {
    id: string;
    data: {
        id: string;
        name: string;
        icon_key: string | undefined;
        link_to_id: string | undefined;
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
