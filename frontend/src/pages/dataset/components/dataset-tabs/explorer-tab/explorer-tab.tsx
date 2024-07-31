import { Edge, Node, XYPosition } from 'reactflow';
import { useEffect } from 'react';
import { Button, Flex } from 'antd';
import styles from './explorer-tab.module.scss';
import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { DatasetNodeProps } from '@/components/charts/custom-nodes/dataset-node/dataset-node.tsx';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { DataProductLink, DatasetContract } from '@/types/dataset';
import 'reactflow/dist/base.css';
import { useTranslation } from 'react-i18next';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { Link } from 'react-router-dom';
import { DataProductNodeProps } from '@/components/charts/custom-nodes/data-product-node/data-product-node.tsx';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { getDataProductDatasetLinkEdgeStyle } from '@/utils/node-editor.helper.ts';

type Props = {
    datasetId: string;
};

function LinkToDataProductNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDataProductIdPath(id)} className={styles.link}>
            <Button type="default">{t('View data product')}</Button>
        </Link>
    );
}

function generateDatasetNodes(
    dataset: DatasetContract,
    dataProductLinks: DataProductLink[],
    defaultNodePosition: XYPosition,
) {
    const datasetMainNode: Node<DatasetNodeProps> = {
        id: dataset.id,
        position: defaultNodePosition,
        data: { name: dataset.name, id: dataset.id, isMainNode: true },
        draggable: false,
        type: CustomNodeTypes.DatasetNode,
        deletable: false,
    };

    const dataProductNodeLinks: Node<DataProductNodeProps>[] = dataProductLinks?.map((link) => ({
        id: link.id,
        position: defaultNodePosition,
        data: {
            name: link.data_product.name,
            id: link.data_product_id,
            nodeToolbarActions: <LinkToDataProductNode id={link.data_product_id} />,
            icon_key: link.data_product.type.icon_key,
            isActive: link.status === DataProductDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DataProductNode,
        deletable: false,
    }));
    return [datasetMainNode, ...dataProductNodeLinks];
}

function generateDatasetEdges(datasetId: string, dataProductLinks: DataProductLink[]): Edge[] {
    return dataProductLinks.map((link) => ({
        id: `${datasetId}-${link.id}`,
        source: datasetId,
        target: link.id,
        sourceHandle: 'right_s',
        targetHandle: 'left_t',
        animated: link.status === DataProductDatasetLinkStatus.Approved,
        deletable: false,
        style: getDataProductDatasetLinkEdgeStyle(link.status),
    }));
}

export function ExplorerTab({ datasetId }: Props) {
    const { data: dataset, isFetching } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodesAndEdges, defaultNodePosition, setNodes } =
        useNodeEditor();

    const generateGraph = (data: DatasetContract) => {
        const dataset = data;
        const approvedDataProductLinks = dataset.data_product_links.filter(
            (link) => link.status !== DataProductDatasetLinkStatus.Denied,
        );
        const datasetNodes: Node[] = generateDatasetNodes(dataset, approvedDataProductLinks, defaultNodePosition);
        const datasetEdges: Edge[] = generateDatasetEdges(dataset.id, approvedDataProductLinks);
        setNodesAndEdges(datasetNodes, datasetEdges);
    };
    useEffect(() => {
        if (dataset?.data_product_links) {
            generateGraph(dataset);
        }
    }, [dataset?.data_product_links, dataset?.id]);

    useEffect(() => {
        if (dataset) {
            setNodes((prevNodes) => {
                return prevNodes.map((node) => {
                    if (node.id === dataset.id) {
                        return {
                            ...node,
                            data: { ...node.data, name: dataset.name },
                        };
                    }
                    return node;
                });
            });
        }
    }, [dataset?.name]);

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
