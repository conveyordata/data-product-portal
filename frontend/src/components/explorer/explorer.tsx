import '@xyflow/react/dist/base.css';

import type { Edge, Node, XYPosition } from '@xyflow/react';
import { Position, ReactFlowProvider } from '@xyflow/react';
import { Button, Flex, theme } from 'antd';
import { useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { TabKeys as DataOutputTabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetDataOutputGraphDataQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import {
    useGetDataProductGraphDataQuery,
    useGetGraphDataQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetGraphDataQuery } from '@/store/features/datasets/datasets-api-slice';
import { greenThemeConfig } from '@/theme/antd-theme';
import type { EdgeContract, NodeContract } from '@/types/graph/graph-contract.ts';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';

import styles from './explorer.module.scss';
import { Sidebar } from './sidebar';

const { getDesignToken } = theme;

const token = getDesignToken(greenThemeConfig);

type Props = {
    id: string;
    type: 'dataset' | 'dataproduct' | 'dataoutput';
};

function LinkToDataProductNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDataProductIdPath(id, DataProductTabKeys.Explorer)} className={styles.link}>
            <Button type="default">{t('View data product')}</Button>
        </Link>
    );
}

function LinkToDatasetNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDatasetIdPath(id, DatasetTabKeys.Explorer)} className={styles.link}>
            <Button type="default">{t('View dataset')}</Button>
        </Link>
    );
}

function LinkToDataOutputNode({ id, product_id }: { id: string; product_id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDataOutputIdPath(id, product_id, DataOutputTabKeys.Explorer)} className={styles.link}>
            <Button type="default">{t('View data output')}</Button>
        </Link>
    );
}

function parseEdges(edges: EdgeContract[]): Edge[] {
    return edges.map((edge) => {
        return {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            targetHandle: 'left_t',
            sourceHandle: 'right_s',
            animated: edge.animated,
            deletable: false,
            style: {
                strokeDasharray: '5 5',
                stroke: edge.animated ? token.colorPrimary : token.colorPrimaryBorder,
            },
        };
    });
}

function parseNodes(nodes: NodeContract[], defaultNodePosition: XYPosition): Node[] {
    return nodes.map((node) => {
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
            data: {
                name: node.data.name,
                id: node.data.id,
                icon_key: node.data.icon_key,
                isMainNode: node.isMain,
                ...extra_attributes,
            },
        };
    });
}

function InternalFullExplorer() {
    // Same as InternalExplorer but this one does not filter anything, it shows the full graph
    // Also includes a sidebar to select nodes

    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodes, setNodesAndEdges, defaultNodePosition } =
        useNodeEditor();

    const { data: graph, isFetching } = useGetGraphDataQuery('', {
        skip: false,
    });
    const generateGraph = useCallback(() => {
        if (graph) {
            const nodes = parseNodes(graph.nodes, defaultNodePosition);
            const edges = parseEdges(graph.edges);
            setNodesAndEdges(nodes, edges);
        }
    }, [defaultNodePosition, graph, setNodesAndEdges]);
    useEffect(() => {
        generateGraph();
    }, [generateGraph]);
    if (isFetching) {
        return <LoadingSpinner />;
    }
    return (
        <Flex vertical className={styles.nodeWrapper}>
            <Sidebar nodes={nodes} setNodes={setNodes} />
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

function InternalExplorer({ id, type }: Props) {
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
            const edges = parseEdges(graph.edges);
            setNodesAndEdges(nodes, edges);
        }
    }, [defaultNodePosition, graph, setNodesAndEdges]);

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

export function FullExplorer() {
    return (
        <ReactFlowProvider>
            <InternalFullExplorer />
        </ReactFlowProvider>
    );
}
