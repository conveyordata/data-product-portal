import '@xyflow/react/dist/base.css';

import type { Edge, Node } from '@xyflow/react';
import { Position, useReactFlow } from '@xyflow/react';
import { Flex, theme } from 'antd';
import { type MouseEvent, useCallback, useEffect, useState } from 'react';

import { defaultFitViewOptions, NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomEdgeTypes, CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useGetGraphDataQuery } from '@/store/features/graph/graph-api-slice.ts';
import type { NodeContract } from '@/types/graph/graph-contract.ts';
import { parseRegularNode } from '@/utils/node-parser.helper';
import { LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode } from '../explorer/common';
import styles from '../explorer/explorer.module.scss';
import { parseEdges } from '../explorer/utils';
import { Sidebar, type SidebarFilters } from './sidebar/sidebar';
import { useNodeEditor } from './use-node-editor';

function parseFullNodes(nodes: NodeContract[], setNodeId: (id: string) => void): Node[] {
    // Parse regular nodes
    const regularNodes = nodes
        .filter((node) => node.type !== CustomNodeTypes.DomainNode)
        .map((node) => {
            let extra_attributes = {};
            switch (node.type) {
                case CustomNodeTypes.DataProductNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? null : <LinkToDataProductNode id={node.data.id} />,
                        targetHandlePosition: Position.Left,
                        assignments: node.data.assignments,
                    };
                    break;
                case CustomNodeTypes.DatasetNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? '' : <LinkToDatasetNode id={node.data.id} />,
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    };
                    break;
                case CustomNodeTypes.DataOutputNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? (
                            ''
                        ) : (
                            <LinkToDataOutputNode id={node.id} product_id={node.data.link_to_id} />
                        ),
                        sourceHandlePosition: Position.Left,
                        isActive: true,
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    };
                    break;
                default:
                    throw new Error(`Unknown node type: ${node.type}`);
            }
            // For now perma disable domains
            return parseRegularNode(node, setNodeId, false, true, extra_attributes);
        });

    return regularNodes; // Skip domain nodes for clarity and reduced clutter
}

function applyHighlighting(nodes: Node[], edges: Edge[], selectedId: string | null) {
    if (!selectedId) {
        // No selection - all nodes normal
        return {
            highlightedNodes: nodes.map((node) => ({ ...node, data: { ...node.data, dimmed: false } })),
            highlightedEdges: edges.map((edge) => ({ ...edge, data: { ...edge.data, dimmed: false } })),
        };
    }

    // Find directly connected node IDs
    const connectedNodeIds = new Set<string>();
    connectedNodeIds.add(selectedId);

    edges.forEach((edge) => {
        if (edge.source === selectedId) {
            connectedNodeIds.add(edge.target);
        }
        if (edge.target === selectedId) {
            connectedNodeIds.add(edge.source);
        }
    });

    // Apply highlighting to nodes
    const highlightedNodes = nodes.map((node) => ({
        ...node,
        data: {
            ...node.data,
            dimmed: !connectedNodeIds.has(node.id),
        },
        style: {
            ...node.style,
            opacity: connectedNodeIds.has(node.id) ? 1 : 0.3,
            zIndex: connectedNodeIds.has(node.id) ? 10 : 1,
        },
    }));

    // Apply highlighting to edges
    const highlightedEdges = edges.map((edge) => ({
        ...edge,
        data: {
            ...edge.data,
            dimmed: !connectedNodeIds.has(edge.source) || !connectedNodeIds.has(edge.target),
        },
        style: {
            ...edge.style,
            opacity: connectedNodeIds.has(edge.source) && connectedNodeIds.has(edge.target) ? 1 : 0.2,
            zIndex: connectedNodeIds.has(edge.source) && connectedNodeIds.has(edge.target) ? 10 : 1,
        },
    }));

    return { highlightedNodes, highlightedEdges };
}

export default function InternalFullExplorer() {
    // Same as InternalExplorer but this one does not filter anything, it shows the full graph
    // Also includes a sidebar to select nodes

    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodes, setEdges, applyLayout } = useNodeEditor();
    const currentInstance = useReactFlow();
    const { token } = theme.useToken();
    const [sidebarFilters, setSidebarFilters] = useState<SidebarFilters>({
        dataProductsEnabled: true,
        datasetsEnabled: true,
        domainsEnabled: true,
    });

    const [nodeId, setNodeId] = useState<string | null>(null);

    const { data: graph, isFetching } = useGetGraphDataQuery(
        {
            includeDataProducts: sidebarFilters.dataProductsEnabled,
            includeDatasets: sidebarFilters.datasetsEnabled,
            includeDomains: sidebarFilters.domainsEnabled,
        },
        {
            skip: false,
        },
    );

    // Helper function to apply highlighting logic

    const generateGraph = useCallback(async () => {
        if (graph) {
            const nodes = parseFullNodes(graph.nodes, setNodeId);
            const edges = parseEdges(graph.edges, token);

            // Explicitly specify straight edge so it doesn't default to default edge (which is a bezier curve)
            const straightEdges = edges.map((edge) => ({
                ...edge,
                type: CustomEdgeTypes.StraightEdge,
            }));

            // Apply highlighting based on selected node
            const { highlightedNodes, highlightedEdges } = applyHighlighting(nodes, straightEdges, nodeId);

            const positionedNodes = await applyLayout(
                highlightedNodes,
                highlightedEdges,
                sidebarFilters.domainsEnabled,
            );

            setNodes(positionedNodes);
            setEdges(highlightedEdges);
        }
    }, [graph, applyLayout, sidebarFilters, token, setEdges, setNodes, nodeId]);

    useEffect(() => {
        generateGraph();
    }, [generateGraph]);

    useEffect(() => {
        // Give React Flow time to update its internals
        const timeout = setTimeout(() => {
            currentInstance.fitView();
            setNodeId(null); // Reset nodeId when the graph is updated
        }, 50); // 50ms is usually enough

        return () => clearTimeout(timeout);
    }, [currentInstance]);

    // Custom node click handler
    function handleNodeClick(_event: MouseEvent | undefined, node: Node) {
        if (node) {
            setNodeId(node.id);

            setTimeout(() => {
                // Get connected nodes for fitting view
                const connectedNodeIds = new Set<string>();
                connectedNodeIds.add(node.id);

                edges.forEach((edge) => {
                    if (edge.source === node.id) {
                        connectedNodeIds.add(edge.target);
                    }
                    if (edge.target === node.id) {
                        connectedNodeIds.add(edge.source);
                    }
                });

                const connectedNodes = nodes.filter((n) => connectedNodeIds.has(n.id));

                currentInstance.fitView({
                    ...defaultFitViewOptions,
                    nodes: connectedNodes,
                    padding: 0.3,
                });
            }, 150);
        }
    }

    // Function to clear selection
    const handleBackgroundClick = useCallback(() => {
        setNodeId(null);
        setTimeout(() => {
            currentInstance.fitView(defaultFitViewOptions);
        }, 50);
    }, [currentInstance]);

    if (isFetching) {
        return <LoadingSpinner />;
    }

    return (
        <Flex className={styles.nodeWrapper}>
            <Sidebar
                nodes={nodes}
                setNodes={setNodes}
                onFilterChange={setSidebarFilters}
                sidebarFilters={sidebarFilters}
                nodeId={nodeId}
                nodeClick={handleNodeClick}
            />
            <NodeEditor
                nodes={nodes}
                edges={edges}
                onConnect={onConnect}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={handleNodeClick}
                onPaneClick={handleBackgroundClick}
                editorProps={{
                    draggable: false,
                    edgesReconnectable: false,
                    nodesConnectable: false,
                }}
            />
        </Flex>
    );
}
