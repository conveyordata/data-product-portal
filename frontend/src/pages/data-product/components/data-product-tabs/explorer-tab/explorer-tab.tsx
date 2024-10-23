import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { Edge, Node, Position, XYPosition } from 'reactflow';
import { useEffect } from 'react';
import { Button, Flex, theme } from 'antd';
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
import { createDataOutputIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { useTranslation } from 'react-i18next';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { getDataProductDatasetLinkEdgeStyle } from '@/utils/node-editor.helper.ts';
import { DataOutputNodeProps } from '@/components/charts/custom-nodes/dataoutput-node/dataoutput-node';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';
import { greenThemeConfig } from '@/theme/antd-theme';

const { getDesignToken } = theme;

const token = getDesignToken(greenThemeConfig);

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

function LinkToDataOutputNode({ id, product_id }: {id: string, product_id: string}) {
    const { t } = useTranslation();
    return (
        <Link to={createDataOutputIdPath(id, product_id)} className={styles.link}>
            <Button type="default">{t('View data output')}</Button>
        </Link>
    )
}

function generateDataProductOutputNodes(dataProduct: DataProductContract, defaultNodePosition: XYPosition): Node[] {
    const dataOutputNodeLinks: Node<DataOutputNodeProps>[] = dataProduct.data_outputs.map((link) => ({
        id: link.id,
        position: { x: defaultNodePosition.x + 1000, y: defaultNodePosition.y },
        data: {
            name: link.name,
            id: link.id,
            icon_key: link.configuration.configuration_type,
            nodeToolbarActions: <LinkToDataOutputNode id={link.id} product_id={dataProduct.id} />,
            sourceHandlePosition: Position.Left,
            isActive: true,
            //isActive: link.status === DataProductDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DataOutputNode,
        deletable: false,
    }));
    return dataOutputNodeLinks;
}

function generateDataProductOutputEdges(dataProduct: DataProductContract): Edge[] {
    return dataProduct.data_outputs.map((link) => ({
        id: `${link.id}-${dataProduct.id}`,
        // source: link.id,
        sourceHandle: 'right_s',
        // target: dataProduct.id,
        source: dataProduct.id,
        target: link.id,
        animated: true,
        deletable: false,
        style: {
            strokeDasharray: '5 5',
            stroke: token.colorPrimary,
        },
    }));
}

function generateDatasetOutputNodes(
    dataOutput: DataOutputsGetContract,
    datasetLinks: DatasetLink[],
    defaultNodePosition: XYPosition,
): Node[] {
    const datasetNodeLinks: Node<DatasetNodeProps>[] = datasetLinks.map((link) => ({
        id: link.dataset_id + '_for_data_output',
        position: defaultNodePosition,
        data: {
            name: link.dataset.name,
            id: link.dataset_id,
            nodeToolbarActions: <LinkToDatasetNode id={link.dataset_id} />,
            targetHandlePosition: Position.Right,
            targetHandleId: 'left_t',
            isActive: link.status === DataProductDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DatasetNode,
        deletable: false,
    }));
    return datasetNodeLinks;
}

function generateDatasetDataOutputEdges(dataOutputId: string, datasetLinks: DatasetLink[]): Edge[] {
    return datasetLinks.map((link) => ({
        id: `${link.dataset_id}-${dataOutputId}`,
        source: dataOutputId,
        target: link.dataset_id + '_for_data_output',
        targetHandle: 'left_t',
        sourceHandle: 'right_s',
        animated: link.status === DataProductDatasetLinkStatus.Approved,
        deletable: false,
        style: getDataProductDatasetLinkEdgeStyle(link.status),
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
        position: { x: defaultNodePosition.x - 500, y: defaultNodePosition.y },
        data: {
            name: link.dataset.name,
            id: link.dataset_id,
            nodeToolbarActions: <LinkToDatasetNode id={link.dataset_id} />,
            targetHandlePosition: Position.Right,
            targetHandleId: 'left_t',
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
        targetHandle: 'left_t',
        sourceHandle: 'right_s',
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

        const dataProductOutputNodes: Node[] = generateDataProductOutputNodes(dataProduct, defaultNodePosition);

        const combinedNodes = dataProductOutputNodes.concat(
            ...dataProduct.data_outputs.flatMap((data_output) => {
                const approvedDatasetLinks = data_output.dataset_links.filter(
                    (link) => link.status !== DataOutputDatasetLinkStatus.Denied,
                );
                const dataProductNodes: Node[] = generateDatasetOutputNodes(
                    data_output,
                    approvedDatasetLinks,
                    defaultNodePosition,
                );
                // const dataProductEdges: Edge[] = generateDatasetDataOutputEdges(data_output.id, approvedDatasetLinks);

                return dataProductNodes;
            }),
        );
        const dataProductOutputEdges: Edge[] = generateDataProductOutputEdges(dataProduct);
        const combinedEdges = dataProductOutputEdges.concat(
            ...dataProduct.data_outputs.flatMap((data_output) => {
                const approvedDatasetLinks = data_output.dataset_links.filter(
                    (link) => link.status !== DataOutputDatasetLinkStatus.Denied,
                );
                const dataProductEdges: Edge[] = generateDatasetDataOutputEdges(data_output.id, approvedDatasetLinks);
                return dataProductEdges;
            }),
        );
        setNodesAndEdges(dataProductNodes.concat(combinedNodes), dataProductEdges.concat(combinedEdges));
    };

    useEffect(() => {
        if (dataProduct?.dataset_links) {
            generateGraph(dataProduct);
        }
        if (dataProduct?.data_outputs) {
            generateGraph(dataProduct);
        }
    }, [dataProduct?.dataset_links, dataProduct?.id, dataProduct?.data_outputs]);

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
