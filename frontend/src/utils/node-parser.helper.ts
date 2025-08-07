import type { Node, Position, XYPosition } from '@xyflow/react';
import type { NodeContract } from '@/types/graph/graph-contract';
import type { DataProductRoleAssignmentContract } from '@/types/roles/role.contract';

// Define colors for domain nodes
// Should have the same corresponding colors with domainBorderColors for a clean look
const domainBackgroundColors = [
    'rgba(15, 200, 0, 0.1)', // green
    'rgba(0, 0, 255, 0.1)', // blue
    'rgba(255, 0, 0, 0.1)', // red
    'rgba(255, 0, 255, 0.1)', // purple
    'rgba(255, 165, 0, 0.1)', // orange
];
const domainBorderColors = [
    'rgba(15, 200, 0, 0.4)', // green
    'rgba(0, 0, 255, 0.4)', // blue
    'rgba(255, 0, 0, 0.4)', // red
    'rgba(255, 0, 255, 0.4)', // purple
    'rgba(255, 165, 0, 0.4)', // orange
];

function sharedAttributes(node: NodeContract, setNodeId: (id: string) => void, domainsEnabled: boolean): Node {
    return {
        id: node.id,
        position: { x: 0, y: 0 } as XYPosition, // Default position, will be updated later by the layout algorithm
        draggable: true,
        deletable: false,
        type: node.type,
        ...(domainsEnabled && node.data.domain_id
            ? {
                  parentId: node.data.domain_id,
              }
            : {}),
        data: {
            name: node.data.name,
            id: node.data.id,
            icon_key: node.data.icon_key,
            isMainNode: node.isMain,
            description: node.data.description,
            onClick: () => {
                setNodeId(node.id);
            },
        },
    };
}

export function parseRegularNode(
    node: NodeContract,
    setNodeId: (id: string) => void,
    domainsEnabled: boolean,
    extra_attributes: {
        nodeToolbarActions?: React.ReactNode;
        targetHandlePosition?: Position;
        sourceHandlePosition?: Position;
        isActive?: boolean;
        targetHandleId?: string;
        assignments?: DataProductRoleAssignmentContract[];
    },
): Node {
    const parsedNode = sharedAttributes(node, setNodeId, domainsEnabled);
    return {
        ...parsedNode,
        data: {
            domain: node.data.domain,
            ...parsedNode.data,
            ...extra_attributes,
        },
    };
}

export function parseDomainNode(node: NodeContract, setNodeId: (id: string) => void, nodeColorIndex = 0): Node {
    const parsedNode = sharedAttributes(node, setNodeId, false); //trick: set domains to false to not have a parentId
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
