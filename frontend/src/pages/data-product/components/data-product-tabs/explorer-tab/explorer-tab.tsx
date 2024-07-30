import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { Edge, Node, Position, XYPosition } from 'reactflow';
import { useEffect } from 'react';
import { Button, Flex } from 'antd';
import styles from './explorer-tab.module.scss';
import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataProductContract, DatasetLink } from '@/types/data-product';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { DataProductNodeProps } from '@/components/charts/custom-nodes/data-product-node/data-product-node.tsx';
import { DatasetNodeProps } from '@/components/charts/custom-nodes/dataset-node/dataset-node.tsx';
import 'reactflow/dist/base.css';
import { Link } from 'react-router-dom';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { useTranslation } from 'react-i18next';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { getDataProductDatasetLinkEdgeStyle } from '@/utils/node-editor.helper.ts';
import { DataOutputNodeProps } from '@/components/charts/custom-nodes/dataoutput-node/dataoutput-node';

type Props = {
    dataProductId: string;
};

function LinkToDatasetNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDatasetIdPath(id)} className={styles.link}>
            <Button type="default">{t('View dataset')}</Button>
        </Link>
    );
}

function generateDataProductOutputNodes(
    dataProduct: DataProductContract,
    defaultNodePosition: XYPosition,
): Node[] {
    const dataProductMainNode: Node<DataProductNodeProps> = {
        id: dataProduct.id,
        position: defaultNodePosition,
        data: {
            name: dataProduct.name,
            icon_key: dataProduct.type.icon_key,
            id: dataProduct.id,
            isMainNode: true,
            targetHandlePosition: Position.Right,
        },
        draggable: false,
        type: CustomNodeTypes.DataProductNode,
        deletable: false,
    };

    const dataOutputNodeLinks: Node<DataOutputNodeProps>[] = dataProduct.data_outputs.map((link) => ({
        id: link.id,
        position: defaultNodePosition,
        data: {
            name: link.name,
            id: link.id,
            icon: link.configuration_type,
            //nodeToolbarActions: <LinkToDataOutputNode id={link.id} />,
            sourceHandlePosition: Position.Left,
            isActive: true
            //isActive: link.status === DataProductDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DatasetNode,
        deletable: false,
    }));
    return [dataProductMainNode, ...dataOutputNodeLinks];
}

function generateDataProductOutputEdges(dataProduct: DataProductContract): Edge[] {
    return dataProduct.data_outputs.map((link) => ({
        id: `${link.id}-${dataProduct.id}`,
        source: link.id,
        targetHandle: "right_t",
        target: dataProduct.id,
        animated: true,
        deletable: false,
        //style: getDataProductDatasetLinkEdgeStyle(link.status),
    }));
}

function generateDataProductNodes(
    dataProduct: DataProductContract,
    datasetLinks: DatasetLink[],
    defaultNodePosition: XYPosition,
): Node[] {
    const dataProductMainNode: Node<DataProductNodeProps> = {
        id: dataProduct.id,
        position: defaultNodePosition,
        data: {
            name: dataProduct.name,
            icon_key: dataProduct.type.icon_key,
            id: dataProduct.id,
            isMainNode: true,
            targetHandlePosition: Position.Left,
        },
        draggable: false,
        type: CustomNodeTypes.DataProductNode,
        deletable: false,
    };

    const datasetNodeLinks: Node<DatasetNodeProps>[] = datasetLinks.map((link) => ({
        id: link.id,
        position: defaultNodePosition,
        data: {
            name: link.dataset.name,
            id: link.dataset_id,
            nodeToolbarActions: <LinkToDatasetNode id={link.dataset_id} />,
            sourceHandlePosition: Position.Right,
            isActive: link.status === DataProductDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DatasetNode,
        deletable: false,
    }));
    return [dataProductMainNode, ...datasetNodeLinks];
}

function generateDataProductEdges(dataProductId: string, datasetLinks: DatasetLink[]): Edge[] {
    return datasetLinks.map((link) => ({
        id: `${link.id}-${dataProductId}`,
        source: link.id,
        target: dataProductId,
        animated: link.status === DataProductDatasetLinkStatus.Approved,
        deletable: false,
        style: getDataProductDatasetLinkEdgeStyle(link.status),
    }));
}

export function ExplorerTab({ dataProductId }: Props) {
    const { data: dataProduct, isFetching } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodesAndEdges, defaultNodePosition, setNodes } =
        useNodeEditor();

    const generateGraph = (data: DataProductContract) => {
        const dataProduct = data;
        const approvedDatasetLinks = dataProduct.dataset_links.filter(
            (link) => link.status !== DataProductDatasetLinkStatus.Denied,
        );
        const dataProductNodes: Node[] = generateDataProductNodes(
            dataProduct,
            approvedDatasetLinks,
            defaultNodePosition,
        );
        const dataProductEdges: Edge[] = generateDataProductEdges(dataProduct.id, approvedDatasetLinks);
        //setNodesAndEdges(dataProductNodes, dataProductEdges, Position.Left);

        const dataProductOutputNodes: Node[] = generateDataProductOutputNodes(
            dataProduct,
            defaultNodePosition
        )
        const dataProductOutputEdges: Edge[] = generateDataProductOutputEdges(dataProduct);
        setNodesAndEdges(dataProductOutputNodes.concat(dataProductNodes), dataProductOutputEdges.concat(dataProductEdges));//, Position.Right);
    };

    useEffect(() => {
        if (dataProduct?.dataset_links) {
            generateGraph(dataProduct);
        }
    }, [dataProduct?.dataset_links, dataProduct?.id]);

    useEffect(() => {
        if (dataProduct) {
            setNodes((prevNodes) => {
                return prevNodes.map((node) => {
                    if (node.id === dataProduct?.id) {
                        return {
                            ...node,
                            data: { ...node.data, name: dataProduct.name },
                        };
                    }
                    return node;
                });
            });
        }
    }, [dataProduct?.name]);

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
