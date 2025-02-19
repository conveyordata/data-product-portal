import { defaultFitViewOptions, generateDagreLayout } from '@/utils/node-editor.helper.ts';
import {
    addEdge,
    Connection,
    Edge,
    Node,
    OnConnect,
    Position,
    useEdgesState,
    useNodesState,
    useReactFlow,
} from 'reactflow';
import { useCallback, useEffect } from 'react';

const defaultNodeWidth = 180;
const defaultNodeHeight = 80;
const defaultNodePosition = { x: 0, y: 0 };
const defaultDirection = Position.Left;

export function useNodeEditor() {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const { fitView } = useReactFlow();

    const setNodesAndEdges = useCallback(
        (nodes: Node[], edges: Edge[], direction: Position = defaultDirection) => {
            const layouted = generateDagreLayout(nodes, edges, direction, defaultNodeWidth, defaultNodeHeight);

            setNodes([...layouted.nodes]);
            setEdges([...layouted.edges]);
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

    useEffect(() => {
        window.requestAnimationFrame(() => {
            fitView(defaultFitViewOptions);
        });
    }, [nodes, edges, fitView]);

    return {
        setNodesAndEdges,
        setNodes,
        setEdges,
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
        defaultNodePosition,
    };
}
