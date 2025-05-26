import '@xyflow/react/dist/base.css';

import type { Node, XYPosition } from '@xyflow/react';
import { Position, ReactFlowProvider } from '@xyflow/react';
import { Flex, theme } from 'antd';
import { useCallback, useEffect } from 'react';

import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { useGetDataOutputGraphDataQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductGraphDataQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetGraphDataQuery } from '@/store/features/datasets/datasets-api-slice';
import type { NodeContract } from '@/types/graph/graph-contract.ts';

import { LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode } from './common.tsx';
import styles from './explorer.module.scss';
import { parseEdges } from './utils.tsx';

type Props = {
    id: string;
    type: 'dataset' | 'dataproduct' | 'dataoutput' | 'domain';
};

function parseNodes(nodes: NodeContract[], defaultNodePosition: XYPosition): Node[] {
    // TODO: revert to old parseNodes function - separate from parseFullNodes
    // Regular nodes and domain nodes. In domain nodes, we count how many children they have so we can estimate their size.
    const regular_nodes = nodes
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
                        assignments: node.data.assignments,
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
                parentId: '672debaf-31f9-4233-820b-ad2165af044e', // TODO: needs to be the id of the domain node
                extent: 'parent', // node not draggable outside of the parent
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
    const childCounts = regular_nodes.reduce((acc: Record<string, number>, node) => {
        if (node.parentId) {
            if (!acc[node.parentId]) {
                acc[node.parentId] = 0;
            }
            acc[node.parentId]++;
        }
        return acc;
    }, {});

    const domain_nodes = nodes
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
        });

    const result = [...domain_nodes, ...regular_nodes];

    console.log('result', result);
    return result;
}

function InternalExplorer({ id, type }: Props) {
    const { token } = theme.useToken();
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodesAndEdges, defaultNodePosition } =
        useNodeEditor();

    const dataProductQuery = useGetDataProductGraphDataQuery(id, { skip: type !== 'dataproduct' || !id });
    const datasetQuery = useGetDatasetGraphDataQuery(id, { skip: type !== 'dataset' || !id });
    const dataOutputQuery = useGetDataOutputGraphDataQuery(id, { skip: type !== 'dataoutput' || !id });

    let graphDataQuery;

    switch (type) {
        case 'dataproduct':
            graphDataQuery = dataProductQuery;
            break;
        case 'dataset':
            graphDataQuery = datasetQuery;
            break;
        case 'dataoutput':
            graphDataQuery = dataOutputQuery;
            break;
    }

    const { data: graph, isFetching } = graphDataQuery;
    const generateGraph = useCallback(() => {
        if (graph) {
            const nodes = parseNodes(graph.nodes, defaultNodePosition);
            const edges = parseEdges(graph.edges, token);
            setNodesAndEdges(nodes, edges);
        }
    }, [defaultNodePosition, graph, setNodesAndEdges, token]);

    useEffect(() => {
        generateGraph();
    }, [generateGraph]);

    if (isFetching) {
        return <LoadingSpinner />;
    }

    return (
        <Flex vertical className={styles.nodeWrapper}>
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

export function Explorer(props: Props) {
    return (
        <ReactFlowProvider>
            <InternalExplorer {...props} />
        </ReactFlowProvider>
    );
}
