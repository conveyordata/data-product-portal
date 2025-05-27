import type { Edge } from '@xyflow/react';
import { GlobalToken } from 'antd';

import type { EdgeContract } from '@/types/graph/graph-contract.ts';

function parseEdges(edges: EdgeContract[], token: GlobalToken): Edge[] {
    return edges.map((edge) => {
        return {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            targetHandle: 'left_t',
            sourceHandle: 'right_s',
            animated: edge.animated,
            deletable: false,
            style: {
                strokeDasharray: '5 5',
                stroke: edge.animated ? token.colorPrimary : token.colorPrimaryBorder,
            },
        };
    });
}

export { parseEdges };
