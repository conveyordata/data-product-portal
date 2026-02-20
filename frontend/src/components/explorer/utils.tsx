import type { Edge } from '@xyflow/react';
import type { GlobalToken } from 'antd';

import type { Edge as GraphEdge } from '@/store/api/services/generated/graphApi.ts';

function parseEdges(edges: GraphEdge[], token: GlobalToken): Edge[] {
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
