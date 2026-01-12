import {
    addEdge,
    type Connection,
    type Edge,
    type Node,
    type OnConnect,
    Position,
    useEdgesState,
    useNodesState,
} from '@xyflow/react';
import { useCallback } from 'react';
import { generateDagreLayout } from '@/utils/node-editor.helper';

// gets node width and height from base-node.module.scss
const getNodeDimensions = () => {
    const style = getComputedStyle(document.documentElement);
    return {
        width: Number.parseInt(style.getPropertyValue('--node-width'), 10),
        height: Number.parseInt(style.getPropertyValue('--node-height'), 10),
    };
};

const defaultDirection = Position.Left;
const { width: defaultNodeWidth, height: defaultNodeHeight } = getNodeDimensions();

export function useNodeEditor() {
    const [nodes, setNodes, onNodesChange] = useNodesState([] as Node[]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([] as Edge[]);

    const applyLayout = useCallback(
        (nodes: Node[], edges: Edge[], direction: Position = defaultDirection) => {
            const layouted = generateDagreLayout(nodes, edges, direction, defaultNodeWidth, defaultNodeHeight);

            setNodes([...layouted.nodes]);
            setEdges([...layouted.edges]);
            return layouted.nodes;
        },
        [setEdges, setNodes],
    );
    const onConnect: OnConnect = useCallback(
        (params: Connection) => {
            const edge = { ...params, animated: true };
            setEdges((eds) => addEdge(edge, eds));
        },
        [setEdges],
    );

    return {
        applyLayout,
        setNodes,
        setEdges,
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
    };
}
