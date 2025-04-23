import type { Connection, Edge, Node, OnConnect } from '@xyflow/react';
import { addEdge, Position, useEdgesState, useNodesState } from '@xyflow/react';
import { useCallback } from 'react';

import { generateDagreLayout } from '@/utils/node-editor.helper.ts';

const defaultNodeWidth = 180;
const defaultNodeHeight = 80;
const defaultNodePosition = { x: 0, y: 0 };
const defaultDirection = Position.Left;

export function useNodeEditor() {
    const [nodes, setNodes, onNodesChange] = useNodesState([] as Node[]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([] as Edge[]);
    // const { fitView } = useReactFlow();

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

    // useEffect(() => {
    //     window.requestAnimationFrame(() => fitView(defaultFitViewOptions));
    // }, [nodes, edges, fitView]);

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
