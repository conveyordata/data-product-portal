import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { Edge, Node, Position, XYPosition } from 'reactflow';
import { useEffect } from 'react';
import { Button, Flex, theme } from 'antd';
import styles from './explorer-tab.module.scss';
import { NodeEditor } from '@/components/charts/node-editor/node-editor.tsx';
import { useNodeEditor } from '@/hooks/use-node-editor.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
// import { DataOutputContract, DatasetLink } from '@/types/data-output';
import { CustomNodeTypes } from '@/components/charts/node-editor/node-types.ts';
// import { DataOutputNodeProps } from '@/components/charts/custom-nodes/data-output-node/data-output-node.tsx';
import { DatasetNodeProps } from '@/components/charts/custom-nodes/dataset-node/dataset-node.tsx';
import 'reactflow/dist/base.css';
import { Link } from 'react-router-dom';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { useTranslation } from 'react-i18next';
// import { getDataOutputDatasetLinkEdgeStyle } from '@/utils/node-editor.helper.ts';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';
import { greenThemeConfig } from '@/theme/antd-theme';

const { getDesignToken } = theme;

const token = getDesignToken(greenThemeConfig);

type Props = {
    dataOutputId: string;
};

function LinkToDatasetNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDatasetIdPath(id)} className={styles.link}>
            <Button type="default">{t('View dataset')}</Button>
        </Link>
    );
}

function generateDataOutputOutputNodes(dataOutput: DataOutputContract, defaultNodePosition: XYPosition): Node[] {
    const dataOutputNodeLinks: Node<DataOutputNodeProps>[] = dataOutput.data_outputs.map((link) => ({
        id: link.id,
        position: { x: defaultNodePosition.x + 1000, y: defaultNodePosition.y },
        data: {
            name: link.name,
            id: link.id,
            icon_key: link.configuration_type,
            //nodeToolbarActions: <LinkToDataOutputNode id={link.id} />,
            sourceHandlePosition: Position.Left,
            isActive: true,
            //isActive: link.status === DataOutputDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DataOutputNode,
        deletable: false,
    }));
    return dataOutputNodeLinks;
}

function generateDataOutputOutputEdges(dataOutput: DataOutputContract): Edge[] {
    return dataOutput.data_outputs.map((link) => ({
        id: `${link.id}-${dataOutput.id}`,
        // source: link.id,
        sourceHandle: 'right_s',
        // target: dataOutput.id,
        source: dataOutput.id,
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
            isActive: link.status === DataOutputDatasetLinkStatus.Approved,
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
        animated: link.status === DataOutputDatasetLinkStatus.Approved,
        deletable: false,
        style: getDataOutputDatasetLinkEdgeStyle(link.status),
    }));
}

function generateDataOutputNodes(
    dataOutput: DataOutputContract,
    datasetLinks: DatasetLink[],
    defaultNodePosition: XYPosition,
): Node[] {
    const dataOutputMainNode: Node<DataOutputNodeProps> = {
        id: dataOutput.id,
        position: defaultNodePosition,
        data: {
            name: dataOutput.name,
            icon_key: dataOutput.type.icon_key,
            id: dataOutput.id,
            isMainNode: true,
            targetHandlePosition: Position.Left,
        },
        draggable: false,
        type: CustomNodeTypes.DataOutputNode,
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
            isActive: link.status === DataOutputDatasetLinkStatus.Approved,
        },
        draggable: false,
        type: CustomNodeTypes.DatasetNode,
        deletable: false,
    }));
    return [dataOutputMainNode, ...datasetNodeLinks];
}

function generateDataOutputEdges(dataOutputId: string, datasetLinks: DatasetLink[]): Edge[] {
    return datasetLinks.map((link) => ({
        id: `${link.id}-${dataOutputId}`,
        source: link.id,
        target: dataOutputId,
        targetHandle: 'left_t',
        sourceHandle: 'right_s',
        animated: link.status === DataOutputDatasetLinkStatus.Approved,
        deletable: false,
        style: getDataOutputDatasetLinkEdgeStyle(link.status),
    }));
}

export function ExplorerTab({ dataOutputId }: Props) {
    const { data: dataOutput, isFetching } = useGetDataOutputByIdQuery(dataOutputId, { skip: !dataOutputId });
    const { edges, onEdgesChange, nodes, onNodesChange, onConnect, setNodesAndEdges, defaultNodePosition, setNodes } =
        useNodeEditor();

    const generateGraph = (data: DataOutputContract) => {
        const dataOutput = data;
        const approvedDatasetLinks = dataOutput.dataset_links.filter(
            (link) => link.status !== DataOutputDatasetLinkStatus.Denied,
        );
        const dataOutputNodes: Node[] = generateDataOutputNodes(
            dataOutput,
            approvedDatasetLinks,
            defaultNodePosition,
        );
        const dataOutputEdges: Edge[] = generateDataOutputEdges(dataOutput.id, approvedDatasetLinks);
        //setNodesAndEdges(dataOutputNodes, dataOutputEdges, Position.Left);

        const dataOutputOutputNodes: Node[] = generateDataOutputOutputNodes(dataOutput, defaultNodePosition);

        const combinedNodes = dataOutputOutputNodes.concat(
            ...dataOutput.data_outputs.flatMap((data_output) => {
                const approvedDatasetLinks = data_output.dataset_links.filter(
                    (link) => link.status !== DataOutputDatasetLinkStatus.Denied,
                );
                const dataOutputNodes: Node[] = generateDatasetOutputNodes(
                    data_output,
                    approvedDatasetLinks,
                    defaultNodePosition,
                );
                // const dataOutputEdges: Edge[] = generateDatasetDataOutputEdges(data_output.id, approvedDatasetLinks);

                return dataOutputNodes;
            }),
        );
        const dataOutputOutputEdges: Edge[] = generateDataOutputOutputEdges(dataOutput);
        const combinedEdges = dataOutputOutputEdges.concat(
            ...dataOutput.data_outputs.flatMap((data_output) => {
                const approvedDatasetLinks = data_output.dataset_links.filter(
                    (link) => link.status !== DataOutputDatasetLinkStatus.Denied,
                );
                const dataOutputEdges: Edge[] = generateDatasetDataOutputEdges(data_output.id, approvedDatasetLinks);
                return dataOutputEdges;
            }),
        );
        setNodesAndEdges(dataOutputNodes.concat(combinedNodes), dataOutputEdges.concat(combinedEdges));
    };

    useEffect(() => {
        if (dataOutput?.dataset_links) {
            generateGraph(dataOutput);
        }
        if (dataOutput?.data_outputs) {
            generateGraph(dataOutput);
        }
    }, [dataOutput?.dataset_links, dataOutput?.id, dataOutput?.data_outputs]);

    useEffect(() => {
        if (dataOutput) {
            setNodes((prevNodes) => {
                return prevNodes.map((node) => {
                    if (node.id === dataOutput?.id) {
                        return {
                            ...node,
                            data: { ...node.data, name: dataOutput.name },
                        };
                    }
                    return node;
                });
            });
        }
    }, [dataOutput?.name]);

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
