import type { Connection, Edge, Node, OnConnect } from '@xyflow/react';
import { addEdge, useEdgesState, useNodesState } from '@xyflow/react';
import { useCallback } from 'react';
import ELK from 'elkjs';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types';

const defaultNodeWidth = 80;
const defaultNodeHeight = 80;
const defaultNodePosition = { x: 0, y: 0 };

export function useNodeEditor() {
    const [nodes, setNodes, onNodesChange] = useNodesState([] as Node[]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([] as Edge[]);
    // const { fitView } = useReactFlow();

    const applyLayout = useCallback(
        async (nodes: Node[], edges: Edge[], advancedLayout: boolean = false) => {
            const elkedNodes = await applyElkLayout(nodes, edges, advancedLayout);
            return elkedNodes;
        },
        [],
    );

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
        defaultNodePosition,
    };
}

const basicLayoutOptions = {
    // Core algorithm
    "elk.algorithm": "layered",
    "elk.direction": "RIGHT",

    // Spacing options (use string values, not numbers)
    "elk.spacing.nodeNode": "80.0",
    "elk.spacing.edgeNode": "40.0",
    "elk.spacing.edgeEdge": "20.0",

    // Layered algorithm specific options
    "elk.layered.spacing.nodeNodeBetweenLayers": "100.0",
    "elk.layered.spacing.edgeNodeBetweenLayers": "50.0",
    "elk.layered.nodePlacement.strategy": "SIMPLE",
    "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",

    // Port constraints
    "elk.portConstraints": "FIXED_SIDE",

    // Padding
    "elk.padding": "[top=50.0,left=50.0,bottom=50.0,right=50.0]",
}

const advancedLayoutOptions = {
  "elk.algorithm": "force",
  "elk.force.repulsivePower": "1.5",
  "elk.force.model": "FRUCHTERMAN_REINGOLD",
  "elk.force.iterations": "300",
  "elk.force.repulsion": "200.0",
  "elk.hierarchyHandling": "INCLUDE_CHILDREN",
  "elk.spacing.nodeNode": "60.0", // Spacing between domain nodes
  "elk.padding": "[top=20.0,left=20.0,bottom=20.0,right=20.0]",
  "elk.aspectRatio": "1.0",
  "elk.compaction.connectedComponents": "true",
}

// const advancedLayoutOptions = {
//   "elk.algorithm": "stress",
//   "elk.stress.iterationLimit": "1000",
//   "elk.stress.epsilon": "0.0001",
//   "elk.stress.desiredEdgeLength": "100.0",
//   "elk.hierarchyHandling": "INCLUDE_CHILDREN",
//   "elk.spacing.nodeNode": "60.0",
//   "elk.padding": "[top=40.0,left=30.0,bottom=30.0,right=30.0]",
//   "elk.aspectRatio": "1.0",
// }

async function applyElkLayout(nodes: Node[], edges: Edge[], advancedLayout: boolean): Promise<Node[]> {
    const elk = new ELK();

    interface ElkEdge {
        id: string
        sources: string[]
        targets: string[]
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
                layoutOptions: {
          "elk.algorithm": "force",
          "elk.spacing.nodeNode": "30.0",
          "elk.padding": "[top=30.0,left=30.0,bottom=30.0,right=30.0]",
        },
            }
        } else {
            // Regular node
            return {
                id: parentNode.id,
                width: defaultNodeWidth,
                height: defaultNodeHeight,
            }
        }
        });

    // build graph that elk understands (using only necessary info)
    const elkGraph = {
        id: "root",
        layoutOptions: advancedLayout? advancedLayoutOptions : basicLayoutOptions,
        children: graphChildren,
        edges: edges.map((edge): ElkEdge => ({
            id: edge.id,
            sources: [edge.source],
            targets: [edge.target],
        })),
    };

    // Calculate the layout
    const layout = await elk.layout(elkGraph);
    console.log("ELK layout calculated:", layout);

    // Map the layout positions back to the nodes 
    // (e.g. instert positions of the nodes (override default position) + set size for domain nodes)
    const elkedNodes: Node[] = [];

    layout.children?.forEach((layoutNode: any) => {
        const node = nodes.find((n) => n.id === layoutNode.id)
        if (!node) return; // happens for children of domain nodes (not top level)

        if (node.type === CustomNodeTypes.DomainNode) {
            console.log(`Domain node ${node.data.name}:`, {
                elkCalculated: { width: layoutNode.width, height: layoutNode.height },
                position: { x: layoutNode.x, y: layoutNode.y },
            })
            // domain node itself
            elkedNodes.push({
                ...node,
                position: {
                    x: layoutNode.x,
                    y: layoutNode.y,
                },
                style: {
                    ...node.style,
                    width: layoutNode.width,
                    height: layoutNode.height,
                },
            });

            // children of domain node
            layoutNode.children?.forEach((childLayoutNode: any) => {
                const childNode = nodes.find((n) => n.id == childLayoutNode.id);
                if (!childNode) { console.warn("A childnode after layout couldn't be found in the original nodes!"); }
                else {
                    elkedNodes.push({
                        ...childNode,
                        position: { // position in layout is absolute
                            x: childLayoutNode.x,
                            y: childLayoutNode.y,
                        }
                    });
                }
            });
        } else {
            // regular node not contained in any domain node
            elkedNodes.push({
                ...node,
                position: {
                    x: layoutNode.x,
                    y: layoutNode.y,
                }
            });
        }

    });

    return elkedNodes;
}
