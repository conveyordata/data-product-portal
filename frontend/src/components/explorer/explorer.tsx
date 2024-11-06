import { useGetDataProductGraphDataQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { Edge, Node, Position, XYPosition } from 'reactflow';
import { useEffect } from 'react';
import { Button, Flex, theme } from 'antd';
import styles from './explorer.module.scss';
import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import 'reactflow/dist/base.css';
import { Link } from 'react-router-dom';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { useTranslation } from 'react-i18next';
import { greenThemeConfig } from '@/theme/antd-theme';
import { NodeContract, EdgeContract } from '@/types/graph/graph-contract.ts';
import { useGetDatasetGraphDataQuery } from '@/store/features/datasets/datasets-api-slice';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabs.tsx';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabs.tsx';

const { getDesignToken } = theme;

const token = getDesignToken(greenThemeConfig);

type Props = {
    id: string;
    type: "dataset" | "dataproduct";
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

function LinkToDataOutputNode({ id, product_id }: {id: string, product_id: string}) {
    const { t } = useTranslation();
    return (
        <Link to={createDataOutputIdPath(id, product_id)} className={styles.link}>
            <Button type="default">{t('View data output')}</Button>
        </Link>
    )
}

function parseEdges(edges: EdgeContract[]): Edge[] {
    return edges.map(edge => {
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
        }
    });
}

function parseNodes(nodes: NodeContract[], defaultNodePosition: XYPosition): Node[] {
    return nodes.map(node => {
        let extra_attributes = {}
        switch (node.type) {
            case CustomNodeTypes.DataOutputNode:
                extra_attributes = {
                    nodeToolbarActions: node.isMain ? "" : <LinkToDataOutputNode id={node.id} product_id={node.data.link_to_id!} />,
                    sourceHandlePosition: Position.Left,
                    isActive: true,
                    targetHandlePosition: Position.Right,
                    targetHandleId: 'left_t',
                }
                break
            case CustomNodeTypes.DatasetNode:
                extra_attributes = {
                    nodeToolbarActions: node.isMain ? "" : <LinkToDatasetNode id={node.data.id} />,
                    targetHandlePosition: Position.Right,
                    targetHandleId: 'left_t',
                }
                break
            case CustomNodeTypes.DataProductNode:
                extra_attributes = {
                    targetHandlePosition: Position.Left,
                    nodeToolbarActions: node.isMain ? "" : <LinkToDataProductNode id={node.data.id} />,
                }
                break
            default:
                break
        }
        return {
            id: node.id,
            position: defaultNodePosition,
            draggable: false,
            deletable: false,
            type: node.type,
            data: {
                name: node.data.name,
                id: node.data.id,
                icon_key: node.data.icon_key,
                isMainNode: node.isMain,
                ...extra_attributes
            },
        }
    })
}
export function Explorer({ id, type }: Props) {
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodesAndEdges, defaultNodePosition } =
        useNodeEditor();

    const {data: graph, isFetching} = type == "dataproduct" ? useGetDataProductGraphDataQuery(id, {skip: !id}) :  useGetDatasetGraphDataQuery(id, {skip: !id}) ;

    const generateGraph = () => {
        if (graph) {
            let nodes = parseNodes(graph.nodes, defaultNodePosition)
            let edges = parseEdges(graph.edges)
            setNodesAndEdges(nodes, edges);
        }
    }

    useEffect(() => {
        generateGraph();
    }, [graph])

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
                    edgesUpdatable: false,
                    nodesConnectable: false,
                }}
            />
        </Flex>
    );
}
