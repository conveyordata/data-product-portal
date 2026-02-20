import '@xyflow/react/dist/base.css';

import type { Node } from '@xyflow/react';
import { Position, ReactFlowProvider } from '@xyflow/react';
import { Flex, theme } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { CustomEdgeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import type { Node as GraphNode } from '@/store/api/services/generated/dataProductsApi.ts';
import { NodeType, useGetDataProductGraphDataQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetOutputPortGraphDataQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetTechnicalAssetGraphDataQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { type UiElementMetadataResponse, useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { parseRegularNode } from '@/utils/node-parser.helper.ts';
import { LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode } from './common.tsx';
import styles from './explorer.module.scss';
import { useNodeEditor } from './use-node-editor.tsx';
import { parseEdges } from './utils.tsx';

type Props = {
    id: string;
    dataProductId?: string;
    type: 'dataset' | 'dataproduct' | 'dataoutput';
};

function parseNodes(nodes: GraphNode[], t: TFunction, plugins: UiElementMetadataResponse[]): Node[] {
    return nodes
        .filter((node) => node.type !== NodeType.DomainNode)
        .map((node) => {
            let extra_attributes = {};
            switch (node.type) {
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
                        plugins: plugins,
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
                case NodeType.DataProductNode:
                    extra_attributes = {
                        targetHandlePosition: Position.Left,
                        nodeToolbarActions: node.isMain ? '' : <LinkToDataProductNode id={node.data.id} />,
                        assignments: node.data.assignments,
                        description: node.data.description,
                    };
                    break;
                default:
                    dispatchMessage({
                        content: t('Unknown node type: {{ nodeType }}', { nodeType: node.type }),
                        type: 'error',
                    });
            }

            return parseRegularNode(
                node,
                () => {
                    /*no sidebar with node info so no need for nodeId*/
                },
                false,
                false,
                extra_attributes,
            );
        });
}

function InternalExplorer({ id, type, dataProductId }: Props) {
    const { token } = theme.useToken();
    const { data: plugins } = useGetPluginsQuery();
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodes, setEdges, applyLayout } = useNodeEditor();
    const { t } = useTranslation();
    const { data: dataProductQuery, isFetching: isFetchingDataProduct } = useGetDataProductGraphDataQuery(
        { id },
        { skip: type !== 'dataproduct' },
    );
    const { data: datasetQuery, isFetching: isFetchingTechnicalAsset } = useGetTechnicalAssetGraphDataQuery(
        { id, dataProductId: dataProductId || '' },
        { skip: type !== 'dataset' || !dataProductId },
    );
    const { data: dataOutputQuery, isFetching: isFetchingOutputPort } = useGetOutputPortGraphDataQuery(
        { id, dataProductId: dataProductId || '' },
        { skip: type !== 'dataoutput' || !dataProductId },
    );

    const graph = useMemo(() => {
        switch (type) {
            case 'dataproduct':
                return dataProductQuery;
            case 'dataset':
                return datasetQuery;
            case 'dataoutput':
                return dataOutputQuery;
            default:
                throw new Error('Unknown type');
        }
    }, [dataProductQuery, datasetQuery, dataOutputQuery, type]);

    const generateGraph = useCallback(() => {
        if (graph) {
            const nodes = parseNodes(graph?.nodes, t, plugins?.plugins || []);
            const edges = parseEdges(graph?.edges, token);

            const straightEdges = edges.map((edge) => ({
                ...edge,
                type: CustomEdgeTypes.DefaultEdge,
            }));

            const positionedNodes = applyLayout(nodes, straightEdges);

            setNodes(positionedNodes);
            setEdges(straightEdges);
        }
    }, [graph, setNodes, setEdges, applyLayout, token, t, plugins]);

    useEffect(() => {
        generateGraph();
    }, [generateGraph]);

    if (isFetchingDataProduct || isFetchingOutputPort || isFetchingTechnicalAsset) {
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
