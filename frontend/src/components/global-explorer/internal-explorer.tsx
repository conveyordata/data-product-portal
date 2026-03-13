import '@xyflow/react/dist/base.css';

import { G2 } from '@ant-design/plots';
import type { Edge, Node } from '@xyflow/react';
import { Position, useReactFlow } from '@xyflow/react';
import { Flex, theme } from 'antd';
import { type MouseEvent, useCallback, useEffect, useState } from 'react';
import { defaultFitViewOptions, NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomEdgeTypes, CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import type { Node as GraphNode } from '@/store/api/services/generated/graphApi.ts';
import { NodeType, useGetGraphDataQuery } from '@/store/api/services/generated/graphApi.ts';
import { parseRegularNode } from '@/utils/node-parser.helper';
import { LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode } from '../explorer/common';
import styles from '../explorer/explorer.module.scss';
import { parseEdges } from '../explorer/utils';
import { Sidebar, type SidebarFilters } from './sidebar/sidebar';
import { useNodeEditor } from './use-node-editor';

function hexToRgba(hex: string, alpha: number): string {
    const r = Number.parseInt(hex.slice(1, 3), 16);
    const g = Number.parseInt(hex.slice(3, 5), 16);
    const b = Number.parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function parseFullNodes(nodes: GraphNode[], setNodeId: (id: string) => void, domainsEnabled: boolean): Node[] {
    const category20 = G2.Light().category20 ?? [];
    if (category20.length === 0) {
        throw new Error('Category20 colors not available');
    }
    // Synthesize domain container nodes
    const domainNodes: Node[] = [];
    if (domainsEnabled) {
        const domainMap = new Map<string, string>();
        for (const node of nodes) {
            if (node.data.domain_id && node.data.domain && !domainMap.has(node.data.domain_id)) {
                domainMap.set(node.data.domain_id, node.data.domain);
            }
        }
        const sortedDomainIds = [...domainMap.keys()].sort();
        for (let i = 0; i < sortedDomainIds.length; i++) {
            const domainId = sortedDomainIds[i];
            domainNodes.push({
                id: domainId,
                position: { x: 0, y: 0 },
                type: CustomNodeTypes.DomainNode,
                draggable: true,
                deletable: false,
                data: {
                    id: domainId,
                    name: domainMap.get(domainId),
                    backgroundColor: hexToRgba(category20[i % category20.length], 0.08),
                    borderColor: hexToRgba(category20[i % category20.length], 0.3),
                },
            });
        }
    }

    // Parse regular nodes
    const regularNodes = nodes
        .filter((node) => node.type !== NodeType.DomainNode)
        .map((node) => {
            let extra_attributes = {};
            switch (node.type) {
                case NodeType.DataProductNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? null : <LinkToDataProductNode id={node.data.id} />,
                        targetHandlePosition: Position.Left,
                    };
                    break;
                case NodeType.DatasetNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? (
                            ''
                        ) : (
                            <LinkToDatasetNode id={node.data.id} product_id={node.data.link_to_id || ''} />
                        ),
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    };
                    break;
                case NodeType.DataOutputNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? (
                            ''
                        ) : (
                            <LinkToDataOutputNode id={node.id} product_id={node.data.link_to_id || ''} />
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
            return parseRegularNode(node, setNodeId, domainsEnabled, true, extra_attributes);
        });

    return [...domainNodes, ...regularNodes];
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

    // Domain nodes should stay visible if any of their children are connected
    const domainNodeIds = new Set(nodes.filter((n) => n.type === CustomNodeTypes.DomainNode).map((n) => n.id));
    const activeDomainIds = new Set(
        nodes.filter((n) => n.parentId && connectedNodeIds.has(n.id)).map((n) => n.parentId as string),
    );

    // Apply highlighting to nodes
    const highlightedNodes = nodes.map((node) => {
        const isConnected =
            connectedNodeIds.has(node.id) || (domainNodeIds.has(node.id) && activeDomainIds.has(node.id));
        return {
            ...node,
            data: {
                ...node.data,
                dimmed: !isConnected,
            },
            style: {
                ...node.style,
                opacity: isConnected ? 1 : 0.3,
                zIndex: isConnected ? 10 : 1,
            },
        };
    });

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
    const { token } = theme.useToken();
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodes, setEdges, applyLayout } = useNodeEditor();
    const { fitView } = useReactFlow();

    const [sidebarFilters, setSidebarFilters] = useState<SidebarFilters>({
        dataProductsEnabled: true,
        datasetsEnabled: true,
        domainsEnabled: true,
    });

    const [nodeId, setNodeId] = useState<string | null>(null);

    const { data: graph, isFetching } = useGetGraphDataQuery(
        {
            dataProductNodesEnabled: sidebarFilters.dataProductsEnabled,
            outputPortNodesEnabled: sidebarFilters.datasetsEnabled,
        },
        { skip: false },
    );

    // Helper function to apply highlighting logic

    const generateGraph = useCallback(async () => {
        if (graph) {
            const nodes = parseFullNodes(graph.nodes, setNodeId, sidebarFilters.domainsEnabled);
            const edges = parseEdges(graph.edges, token);

            // Explicitly specify straight edge so it doesn't default to default edge (which is a Bézier curve)
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
            fitView();
            setNodeId(null); // Reset nodeId when the graph is updated
        }, 50); // 50ms is usually enough

        return () => clearTimeout(timeout);
    }, [fitView]);

    // Custom node click handler
    const handleNodeClick = useCallback(
        (_event: MouseEvent | undefined, node: Node) => {
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

                    fitView({
                        ...defaultFitViewOptions,
                        nodes: connectedNodes,
                        padding: 0.3,
                    });
                }, 150);
            }
        },
        [fitView, nodes, edges],
    );

    // Function to clear selection
    const handleBackgroundClick = useCallback(() => {
        setNodeId(null);
        setTimeout(() => fitView(defaultFitViewOptions), 50);
    }, [fitView]);

    return (
        <Flex className={styles.nodeWrapper}>
            <Sidebar
                nodes={nodes}
                onFilterChange={setSidebarFilters}
                sidebarFilters={sidebarFilters}
                nodeId={nodeId}
                nodeClick={handleNodeClick}
            />
            <NodeEditor
                isLoading={isFetching}
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
