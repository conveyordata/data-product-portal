import type { Connection, Edge, Node, OnConnect } from '@xyflow/react';
import { addEdge, useEdgesState, useNodesState } from '@xyflow/react';
import { useCallback } from 'react';
import ELK from 'elkjs';

const defaultNodeWidth = 180;
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
  // Core algorithm
  "elk.algorithm": "layered",
  "elk.direction": "RIGHT",

  // INCREASED SPACING for larger graphs
  "elk.spacing.nodeNode": "50.0",
  "elk.spacing.edgeNode": "10.0", // More space between edges and nodes
  "elk.spacing.edgeEdge": "20.0", 

  // LAYERED ALGORITHM - Better for complex graphs
  "elk.layered.spacing.nodeNodeBetweenLayers": "200.0", // Much more space between layers
  "elk.layered.spacing.edgeNodeBetweenLayers": "100.0", // More edge-to-node spacing between layers

  // ADVANCED NODE PLACEMENT for cleaner layouts
  "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX", // Better than SIMPLE for complex graphs
  "elk.layered.nodePlacement.favorStraightEdges": "true", // Reduces edge bends

  // CROSSING MINIMIZATION - Critical for readability
  "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
  "elk.layered.crossingMinimization.greedySwitch.type": "TWO_SIDED", // Better crossing reduction
  "elk.layered.crossingMinimization.semiInteractive": "true",

  // EDGE ROUTING for smoother edges
  "elk.edgeRouting": "ORTHOGONAL", // Creates clean 90-degree angles
  "elk.layered.edgeRouting.sloppiness": "0.2", // Allows slight curves for better aesthetics

  // CYCLE BREAKING for complex domain graphs
  "elk.layered.cycleBreaking.strategy": "GREEDY", // Handles circular dependencies better

  // PORT CONSTRAINTS - Important for edge cleanliness
  "elk.portConstraints": "FIXED_SIDE",
  "elk.layered.portSortingStrategy": "INPUT_ORDER", // Maintains logical port order

  // COMPACTION for better space utilization
  "elk.layered.compaction.postCompaction.strategy": "LEFT", // Reduces unnecessary whitespace
  "elk.layered.compaction.connectedComponents": "true", // Groups related components

  // THOROUGHNESS - Spend more time for better results
  "elk.layered.thoroughness": "10", // Higher values = better layout (default is 7)

  // PADDING - More generous for complex graphs
  "elk.padding": "[top=100.0,left=100.0,bottom=100.0,right=100.0]",

  // ADDITIONAL TWEAKS for domain-heavy graphs
  "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES", // Respects your node ordering
  "elk.layered.layering.strategy": "NETWORK_SIMPLEX", // Better layer assignment
}

async function applyElkLayout(nodes: Node[], edges: Edge[], advancedLayout: boolean): Promise<Node[]> {
    const elk = new ELK();

    interface ElkNode {
        id: string
        width?: number
        height?: number
        x?: number
        y?: number
    }

    interface ElkEdge {
        id: string
        sources: string[]
        targets: string[]
    }

    const parentNodes = nodes.filter((node) => !node.parentId);
    const childNodes = nodes.filter((node) => node.parentId);

    const graphChildren = parentNodes.map((parentNode) => {
        // If this is a group node (= domain node), include its children
        if (parentNode.type === "group") {
            const children = childNodes.filter((child) => child.parentId === parentNode.id)
                                       .map((child) => ({ id: child.id,
                                                          width: defaultNodeWidth,
                                                          height: defaultNodeHeight,
                                                        }));

            return {
                id: parentNode.id,
                width: Math.max(100, children.length * 200), // Dynamic width based on children
                height: Math.max(100, Math.ceil(children.length / 3) * 150), // Dynamic height
                children: children,
                layoutOptions: {
                    "elk.algorithm": "box", // Use box layout for children within parent
                    "elk.spacing.nodeNode": "50.0",
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
    const elkedNodes: Node[] = [];

    layout.children?.forEach((layoutNode: any) => {
        const node = nodes.find((n) => n.id === layoutNode.id)
        if (!node) return; // for children of domain nodes

        if (node.type === 'group') {
            // domain node itself
            elkedNodes.push({
                ...node,
                position: {
                    x: layoutNode.x,
                    y: layoutNode.y,
                },
                style: {
                    ...node.style,
                    width: layoutNode.width - 60,
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
                        position: { // position in layout: relative -> position in react flow: absolute
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
