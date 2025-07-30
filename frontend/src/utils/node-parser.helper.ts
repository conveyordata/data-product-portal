import type { Node, XYPosition } from "@xyflow/react"
import type { NodeContract } from "@/types/graph/graph-contract"

// Separate parser for Regular nodes and Domain nodes
export class NodeParsers {
    static sharedAttributes(
        node: NodeContract,
        setNodeId: (id: string) => void,
        defaultPosition: XYPosition,
        domainsEnabled: boolean,
    ): Node {
        return {
            id: node.id,
            position: defaultPosition,
            draggable: true,
            deletable: false,
            type: node.type,
            ...(domainsEnabled && node.data.domain_id ? {
                parentId: node.data.domain_id,
            } : {}),
            data: {
                name: node.data.name,
                id: node.data.id,
                icon_key: node.data.icon_key,
                isMainNode: node.isMain,
                description: node.data.description,
                onClick: () => { setNodeId(node.id) },
            }
        }
    }

    static parseRegularNode(
        node: NodeContract,
        setNodeId: (id: string) => void,
        defaultPosition: XYPosition,
        domainsEnabled: boolean,
        extra_attributes: any,
    ): Node {
        const parsedNode = this.sharedAttributes(node, setNodeId, defaultPosition, domainsEnabled);
        return {
            ...parsedNode,
            data: {
                domain: node.data.domain,
                ...parsedNode.data,
                ...extra_attributes,
            }
        };
    }

    static parseDomainNode(
        node: NodeContract,
        setNodeId: (id: string) => void,
        defaultPosition: XYPosition,
    ): Node {
        const parsedNode = this.sharedAttributes(node, setNodeId, defaultPosition, false); //trick: set domains to false to not have a parentId
        return {
            ...parsedNode,
            // style: {
            //     width: 500, // constant size for testing
            //     height: 500,
            //     backgroundColor: 'rgba(238, 255, 0, 0.1)',
            //     border: '1px solid rgba(0, 255, 42, 0.5)',
            //     borderRadius: '8em',
            // },
            data: {
                ...parsedNode.data,
                extent: 'parent',
                type: 'group',
            }
        };
    }
}
