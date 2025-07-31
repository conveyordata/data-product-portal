import '@xyflow/react/dist/base.css';

import type { Node, XYPosition } from '@xyflow/react';
import { Position, ReactFlowProvider, useReactFlow } from '@xyflow/react';
import { Flex, theme } from 'antd';
import { useCallback, useEffect, useState } from 'react';

import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomEdgeTypes, CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { useGetGraphDataQuery } from '@/store/features/graph/graph-api-slice.ts';
import type { NodeContract } from '@/types/graph/graph-contract.ts';

import { LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode } from './common';
import styles from './explorer.module.scss';
import { Sidebar, type SidebarFilters } from './sidebar';
import { parseEdges } from './utils';
import { NodeParsers } from '@/utils/node-parser.helper';

function parseFullNodes(
    nodes: NodeContract[],
    setNodeId: (id: string) => void,
    defaultNodePosition: XYPosition,
    domainsEnabled = true,
): Node[] {

    // Count how many children each domain node has
    let childCounts = nodes
        .filter((node) => node.type !== CustomNodeTypes.DomainNode)
        .reduce((acc: Record<string, number>, node) => {
            if (node.data.domain_id) {
                acc[node.data.domain_id] = (acc[node.data.domain_id] || 0) + 1;
            }
            return acc;
    }, {});

    // Parse regular nodes
    const regularNodes = nodes
        .filter((node) => node.type !== CustomNodeTypes.DomainNode)
        .map((node) => {
            let extra_attributes = {};
            switch (node.type) {
                case CustomNodeTypes.DataProductNode:
                    extra_attributes = { 
                            targetHandlePosition: Position.Left,
                            assignments: node.data.assignments,
                            nodeToolbarActions: node.isMain ? null : <LinkToDataProductNode id={node.data.id} />,
                        }
                    break;
                case CustomNodeTypes.DatasetNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? '' : <LinkToDatasetNode id={node.data.id} />,
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    }
                    break;
                case CustomNodeTypes.DataOutputNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? ('') : <LinkToDataOutputNode id={node.id} product_id={node.data.link_to_id} />,
                        sourceHandlePosition: Position.Left,
                        isActive: true,
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    }
                    break;
                default:
                    throw new Error(`Unknown node type: ${node.type}`)
            }
            return NodeParsers.parseRegularNode(node, setNodeId, defaultNodePosition, domainsEnabled, extra_attributes);
        });

    // Parse domain nodes (only if domains are enabled and they have children)
    const domainNodes = domainsEnabled 
    ? nodes
        .filter((node) => node.type === CustomNodeTypes.DomainNode && childCounts[node.id] > 0)
        .map((node, index) => NodeParsers.parseDomainNode(node, setNodeId, defaultNodePosition, index))
    : []

    console.log(regularNodes);
    
    // domain nodes are parents so should come before their children in the array
    const result = [...domainNodes, ...regularNodes];

    return result;
}

function InternalFullExplorer() {
    // Same as InternalExplorer but this one does not filter anything, it shows the full graph
    // Also includes a sidebar to select nodes

    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodes, setEdges, applyLayout, defaultNodePosition } =
        useNodeEditor();
    const currentInstance = useReactFlow();
    const { token } = theme.useToken();
    const [sidebarFilters, setSidebarFilters] = useState<SidebarFilters>({
        dataProductsEnabled: true,
        datasetsEnabled: true,
        dataOutputsEnabled: true,
        domainsEnabled: true,
    });

    useEffect(() => {
        // Give React Flow time to update its internals
        const timeout = setTimeout(() => {
            currentInstance.fitView();
            setNodeId(null); // Reset nodeId when the graph is updated
        }, 50); // 50ms is usually enough

        return () => clearTimeout(timeout);
    }, [currentInstance]);

    const [nodeId, setNodeId] = useState<string | null>(null);

    const { data: graph, isFetching } = useGetGraphDataQuery(
        {
            includeDataProducts: sidebarFilters.dataProductsEnabled,
            includeDatasets: sidebarFilters.datasetsEnabled,
            includeDataOutputs: sidebarFilters.dataOutputsEnabled,
            includeDomains: sidebarFilters.domainsEnabled,
        },
        {
            skip: false,
        },
    );

    const generateGraph = useCallback(async () => {
        if (graph) {
            const nodes = parseFullNodes(graph.nodes, setNodeId, defaultNodePosition, sidebarFilters.domainsEnabled);
            const edges = parseEdges(graph.edges, token);

            const straightEdges = edges.map(edge => ({
                ...edge,
                type: CustomEdgeTypes.StraightEdge,
            }));

            const positionedNodes = await applyLayout(nodes, straightEdges, sidebarFilters.domainsEnabled); // positions the nodes

            setNodes(positionedNodes);
            setEdges(straightEdges);
        }
    }, [defaultNodePosition, graph, applyLayout, sidebarFilters, token]);

    useEffect(() => {
        generateGraph();
    }, [generateGraph]);

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
                setNodeId={setNodeId}
            />
            <NodeEditor
                nodes={nodes}
                edges={edges}
                onConnect={onConnect}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                editorProps={{
                    draggable: false,
                    edgesReconnectable: false,
                    nodesConnectable: false,
                }}
            />
        </Flex>
    );
}

export function FullExplorer() {
    return (
        <ReactFlowProvider>
            <InternalFullExplorer />
        </ReactFlowProvider>
    );
}
