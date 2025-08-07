import type { Connection, Edge, Node, OnConnect } from '@xyflow/react';
import { addEdge, useEdgesState, useNodesState } from '@xyflow/react';
import ELK from 'elkjs';
import { useCallback } from 'react';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types';

// gets node width and height from base-node.module.scss
const getNodeDimensions = () => {
    const style = getComputedStyle(document.documentElement);
    return {
        width: Number.parseInt(style.getPropertyValue('--node-width')),
        height: Number.parseInt(style.getPropertyValue('--node-height')),
    };
};

const { width: defaultNodeWidth, height: defaultNodeHeight } = getNodeDimensions();

export function useNodeEditor() {
    const [nodes, setNodes, onNodesChange] = useNodesState([] as Node[]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([] as Edge[]);
    // const { fitView } = useReactFlow();

    const applyLayout = useCallback(async (nodes: Node[], edges: Edge[], advancedLayout = false) => {
        const elkedNodes = await applyElkLayout(nodes, edges, advancedLayout);
        return elkedNodes;
    }, []);

    const onConnect: OnConnect = useCallback(
        (params: Connection) => {
            const edge = { ...params, animated: true };
            setEdges((eds) => addEdge(edge, eds));
        },
        [setEdges],
    );

    return {
        applyLayout,
        setNodes,
        setEdges,
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
    };
}

// Layout options without domain nodes (e.g. for explorer.tsx).
const basicLayoutOptions = {
    // Core algorithm
    'elk.algorithm': 'layered',
    'elk.direction': 'RIGHT',

    'elk.spacing.nodeNode': '80.0', // spacing between nodes vertically
    'elk.layered.spacing.edgeNodeBetweenLayers': '50.0', // spacing between nodes horizontally

    'elk.layered.nodePlacement.strategy': 'SIMPLE', // keeps the flow simple and symmetrical
    'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',

    // Port constraints
    'elk.portConstraints': 'FIXED_SIDE',

    // Padding
    'elk.padding': '[top=50.0,left=50.0,bottom=50.0,right=50.0]',
};

// Layout options between domain nodes (e.g. for full-explorer.tsx with domain nodes visible).
const interDomainLayoutOptions = {
    'elk.algorithm': 'force',
    'elk.spacing.nodeNode': '60.0', // spacing between domain nodes
    'elk.aspectRatio': '2', // lower => layout more vertical <-> higher => layout more horizontal
};

// Layout options within a domain node.
const intraDomainLayoutOptions = {
    'elk.algorithm': 'force',
    'elk.spacing.nodeNode': '40.0', // spacing between regular nodes within a domain node

    // A bit more padding at the top.
    // Most of the time, the label doesn't take up the whole height of the node, so this trick evens it out for short labels (taking up 1 instead of 2 lines).
    'elk.padding': '[top=50.0,left=30.0,bottom=30.0,right=30.0]', // spacing between edges of the parent node and its children
};

async function applyElkLayout(nodes: Node[], edges: Edge[], advancedLayout: boolean): Promise<Node[]> {
    const elk = new ELK();

    interface ElkNode {
        id: string;
        width?: number;
        height?: number;
        children?: ElkNode[];
        layoutOptions?: {
            'elk.algorithm'?: string;
            'elk.direction'?: string;
            'elk.spacing.nodeNode'?: string;
            'elk.aspectRatio'?: string;
            'elk.layered.spacing.edgeNodeBetweenLayers'?: string;
            'elk.layered.nodePlacement.strategy'?: string;
            'elk.layered.crossingMinimization.strategy'?: string;
            'elk.portConstraints'?: string;
            'elk.padding'?: string;
            // Add any other possible layout options as needed
        };
        x?: number; // optional, as it only exists after the layout
        y?: number; // optional, as it only exists after the layout
    }

    interface ElkEdge {
        id: string;
        sources: string[];
        targets: string[];
    }

    const parentNodes = nodes.filter((node) => !node.parentId);
    const childNodes = nodes.filter((node) => node.parentId);
    const graphChildren = parentNodes.map((parentNode) => {
        if (parentNode.type === CustomNodeTypes.DomainNode) {
            // If this is a domain node, include its children
            const children = childNodes
                .filter((child) => child.parentId === parentNode.id)
                .map((child) => ({
                    id: child.id,
                    width: defaultNodeWidth,
                    height: defaultNodeHeight,
                }));

            return {
                id: parentNode.id,
                children: children,
                layoutOptions: intraDomainLayoutOptions,
            };
        }
        // Regular node
        return {
            id: parentNode.id,
            width: defaultNodeWidth,
            height: defaultNodeHeight,
        };
    });

    // Build graph that elk understands (i.e. using fields and objects that elkjs uses)
    const elkGraph = {
        id: 'root',
        layoutOptions: advancedLayout ? interDomainLayoutOptions : basicLayoutOptions,
        children: graphChildren,
        edges: edges.map(
            (edge): ElkEdge => ({
                id: edge.id,
                sources: [edge.source],
                targets: [edge.target],
            }),
        ),
    };

    // Calculate the layout
    const layout = await elk.layout(elkGraph);

    // Map the layout positions back to our objects of type Node
    // (e.g. inject positions of the nodes (override default position) + set size for domain nodes
    const elkedNodes: Node[] = [];

    layout.children?.forEach((layoutNode: ElkNode) => {
        const node = nodes.find((n) => n.id === layoutNode.id);
        if (!node) return; // happens for children of domain nodes (not top level)

        if (node.type === CustomNodeTypes.DomainNode) {
            // domain node itself
            elkedNodes.push({
                ...node,
                position: {
                    x: layoutNode.x || 0,
                    y: layoutNode.y || 0,
                },
                style: {
                    ...node.style,
                    width: layoutNode.width,
                    height: layoutNode.height,
                },
            });

            // children of domain node
            layoutNode.children?.forEach((childLayoutNode: ElkNode) => {
                const childNode = nodes.find((n) => n.id === childLayoutNode.id);
                if (!childNode) {
                    console.warn("A childnode after layout couldn't be found in the original nodes!");
                } else {
                    elkedNodes.push({
                        ...childNode,
                        position: {
                            // position in layout is absolute
                            x: childLayoutNode.x || 0,
                            y: childLayoutNode.y || 0,
                        },
                    });
                }
            });
        } else {
            // regular node not contained in any domain node
            elkedNodes.push({
                ...node,
                position: {
                    x: layoutNode.x || 0,
                    y: layoutNode.y || 0,
                },
            });
        }
    });

    return elkedNodes;
}
