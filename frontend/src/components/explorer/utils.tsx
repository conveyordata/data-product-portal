import type { Edge } from '@xyflow/react';
import { theme } from 'antd';

import { greenThemeConfig } from '@/theme/antd-theme';
import type { EdgeContract } from '@/types/graph/graph-contract.ts';

const { getDesignToken } = theme;
const token = getDesignToken(greenThemeConfig);

function parseEdges(edges: EdgeContract[]): Edge[] {
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
