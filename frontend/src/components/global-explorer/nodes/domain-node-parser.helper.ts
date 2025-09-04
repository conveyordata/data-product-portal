import type { Node } from '@xyflow/react';
import type { NodeContract } from '@/types/graph/graph-contract';
import { sharedAttributes } from '@/utils/node-parser.helper';

// Define colors for domain nodes
// Should have the same corresponding colors with domainBorderColors for a clean look
const domainBackgroundColors = [
    'rgba(15, 200, 0, 0.1)', // green
    'rgba(0, 0, 255, 0.1)', // blue
    'rgba(255, 0, 0, 0.1)', // red
    'rgba(255, 0, 255, 0.1)', // purple
    'rgba(255, 165, 0, 0.1)', // orange
    'rgba(0, 255, 255, 0.1)', // cyan
    'rgba(255, 192, 203, 0.1)', // pink
    'rgba(128, 0, 128, 0.1)', // dark purple
    'rgba(255, 255, 0, 0.1)', // yellow
    'rgba(165, 42, 42, 0.1)', // brown
    'rgba(0, 128, 0, 0.1)', // dark green
    'rgba(75, 0, 130, 0.1)', // indigo
    'rgba(255, 20, 147, 0.1)', // deep pink
    'rgba(0, 191, 255, 0.1)', // deep sky blue
    'rgba(255, 127, 80, 0.1)', // coral
];
const domainBorderColors = [
    'rgba(15, 200, 0, 0.4)', // green
    'rgba(0, 0, 255, 0.4)', // blue
    'rgba(255, 0, 0, 0.4)', // red
    'rgba(255, 0, 255, 0.4)', // purple
    'rgba(255, 165, 0, 0.4)', // orange
    'rgba(0, 255, 255, 0.4)', // cyan
    'rgba(255, 192, 203, 0.4)', // pink
    'rgba(128, 0, 128, 0.4)', // dark purple
    'rgba(255, 255, 0, 0.4)', // yellow
    'rgba(165, 42, 42, 0.4)', // brown
    'rgba(0, 128, 0, 0.4)', // dark green
    'rgba(75, 0, 130, 0.4)', // indigo
    'rgba(255, 20, 147, 0.4)', // deep pink
    'rgba(0, 191, 255, 0.4)', // deep sky blue
    'rgba(255, 127, 80, 0.4)', // coral
];

export function parseDomainNode(node: NodeContract, setNodeId: (id: string) => void, nodeColorIndex = 0): Node {
    const parsedNode = sharedAttributes(node, setNodeId, false, true); //trick: set domains to false to not have a parentId
    return {
        ...parsedNode,
        data: {
            ...parsedNode.data,
            extent: 'parent',
            type: 'group',

            // sneaky trick to parse colors for domain node to the component, but this isn't a style sheet
            backgroundColor: domainBackgroundColors[nodeColorIndex % domainBackgroundColors.length],
            borderColor: domainBorderColors[nodeColorIndex % domainBorderColors.length],
        },
    };
}
