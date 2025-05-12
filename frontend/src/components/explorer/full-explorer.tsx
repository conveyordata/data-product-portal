import '@xyflow/react/dist/base.css';

import type { Node, XYPosition } from '@xyflow/react';
import { Position, ReactFlowProvider } from '@xyflow/react';
import { Flex } from 'antd';
import { useCallback, useEffect, useState } from 'react';

import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { useGetGraphDataQuery } from '@/store/features/graph/graph-api-slice.ts';
import type { NodeContract } from '@/types/graph/graph-contract.ts';

import styles from './explorer.module.scss';
import { SidebarFilters, Sidebar } from './sidebar';
import { parseEdges, LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode } from './common';

function parseFullNodes(nodes: NodeContract[], defaultNodePosition: XYPosition, domainsEnabled: boolean = true): Node[] {
    // Regular nodes and domain nodes. In domain nodes, we count how many children they have so we can estimate their size.
    let regular_nodes = nodes
        .filter((node) => node.type !== CustomNodeTypes.DomainNode)
        .map((node) => {
            let extra_attributes = {};
            switch (node.type) {
                case CustomNodeTypes.DataOutputNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? (
                            ''
                        ) : (
                            <LinkToDataOutputNode id={node.id} product_id={node.data.link_to_id!} />
                        ),
                        sourceHandlePosition: Position.Left,
                        isActive: true,
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    };
                    break;
                case CustomNodeTypes.DatasetNode:
                    extra_attributes = {
                        nodeToolbarActions: node.isMain ? '' : <LinkToDatasetNode id={node.data.id} />,
                        targetHandlePosition: Position.Right,
                        targetHandleId: 'left_t',
                    };
                    break;
                case CustomNodeTypes.DataProductNode:
                    extra_attributes = {
                        targetHandlePosition: Position.Left,
                        nodeToolbarActions: node.isMain ? '' : <LinkToDataProductNode id={node.data.id} />,
                        members: node.data.members,
                        description: node.data.description,
                    };
                    break;
                default:
                    break;
            }

            return {
                id: node.id,
                position: defaultNodePosition,
                draggable: true,
                deletable: false,
                type: node.type,
                // Only set parentId if domains are enabled
                ...(domainsEnabled ? {
                    parentId: '672debaf-31f9-4233-820b-ad2165af044e', // TODO: needs to be the id of the domain node
                    extent: 'parent', // node not draggable outside of the parent
                } : {}),
                data: {
                    name: node.data.name,
                    id: node.data.id,
                    icon_key: node.data.icon_key,
                    isMainNode: node.isMain,
                    domain: node.data.domain,
                    ...extra_attributes,
                },
            };
        });

    // count how many children each parent has
    let childCounts = regular_nodes.reduce((acc: Record<string, number>, node) => {
        if (node.parentId) {
            if (!acc[node.parentId]) {
                acc[node.parentId] = 0;
            }
            acc[node.parentId]++;
        }
        return acc;
    }, {});

    // Only include domain nodes if domains are enabled
    let domain_nodes = domainsEnabled
        ? nodes
            .filter((node) => node.type === CustomNodeTypes.DomainNode)
            .map((node) => {
                const childCount = childCounts[node.id] || 1;
                const width = Math.max(200, childCount * 120); // Base width of 400px, 200px per child
                return {
                    id: node.id,
                    position: defaultNodePosition,
                    draggable: true,
                    deletable: false,
                    type: 'group', // TODO: double use of the 'type' field by reactflow and ourselves
                    style: {
                        // TODO: calculate this based on the number of nodes in the domain
                        width: width,
                        height: width * 0.6,
                        backgroundColor: 'rgba(0, 255, 42, 0.1)',
                        border: '1px solid rgba(0, 255, 42, 0.5)',
                        borderRadius: '8em',
                    },
                    data: {
                        name: node.data.name,
                        id: node.data.id,
                        icon_key: node.data.icon_key,
                        isMainNode: node.isMain,
                        description: node.data.description,
                        extent: 'parent',
                        type: 'group',
                    },
                };
            })
        : [];

    let result = [...domain_nodes, ...regular_nodes];

    console.log('result', result);
    return result;
}

function InternalFullExplorer() {
    // Same as InternalExplorer but this one does not filter anything, it shows the full graph
    // Also includes a sidebar to select nodes

    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodes, setNodesAndEdges, defaultNodePosition } =
        useNodeEditor();

    const [sidebarFilters, setSidebarFilters] = useState<SidebarFilters>({
        dataProductsEnabled: true,
        datasetsEnabled: true,
        dataOutputsEnabled: true,
        domainsEnabled: true,
    });

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

    const generateGraph = useCallback(() => {
        if (graph) {
            const nodes = parseFullNodes(graph.nodes, defaultNodePosition, sidebarFilters.domainsEnabled);
            const edges = parseEdges(graph.edges);
            setNodesAndEdges(nodes, edges);
        }
    }, [defaultNodePosition, graph, setNodesAndEdges, sidebarFilters.domainsEnabled]);

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
