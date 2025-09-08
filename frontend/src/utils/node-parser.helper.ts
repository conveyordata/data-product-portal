import type { Node, Position, XYPosition } from '@xyflow/react';
import type { NodeContract } from '@/types/graph/graph-contract';
import type { DataProductRoleAssignmentContract } from '@/types/roles/role.contract';

export function sharedAttributes(
    node: NodeContract,
    setNodeId: (id: string) => void,
    domainsEnabled: boolean,
    centeredHandles: boolean,
): Node {
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
            centeredHandles: centeredHandles,
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
    centeredHandles: boolean,
    extra_attributes: {
        nodeToolbarActions?: React.ReactNode;
        targetHandlePosition?: Position;
        sourceHandlePosition?: Position;
        isActive?: boolean;
        targetHandleId?: string;
        assignments?: DataProductRoleAssignmentContract[];
    },
): Node {
    const parsedNode = sharedAttributes(node, setNodeId, domainsEnabled, centeredHandles);
    return {
        ...parsedNode,
        data: {
            domain: node.data.domain,
            ...parsedNode.data,
            ...extra_attributes,
        },
    };
}
