import '@xyflow/react/dist/style.css';

import type { Connection, Edge, EdgeChange, FitViewOptions, Node, NodeChange, ReactFlowProps } from '@xyflow/react';
import { Background, ConnectionLineType, Controls, ReactFlow } from '@xyflow/react';
import { Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { edgeTypes, nodeTypes } from '@/components/charts/node-editor/node-types.ts';

import styles from './node-editor.module.scss';

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 2;

const defaultFitViewOptions: FitViewOptions = {
    padding: 0.1,
    maxZoom: 1.25,
};

type Props = {
    nodes: Node[];
    edges: Edge[];
    onConnect: (connection: Connection) => void;
    onNodesChange: (changes: NodeChange[]) => void;
    onEdgesChange: (changes: EdgeChange[]) => void;
    editorProps?: Omit<ReactFlowProps, 'nodes' | 'edges' | 'onConnect' | 'onNodesChange' | 'onEdgesChange'>;
    debug?: boolean;
};

export function NodeEditor({
    nodes = [],
    edges = [],
    onConnect,
    onNodesChange,
    onEdgesChange,
    debug,
    editorProps,
}: Props) {
    const { t } = useTranslation();
    const memoizedNodes = useMemo(() => nodes, [nodes]);
    const memoizedEdges = useMemo(() => edges, [edges]);
    return (
        <>
            <ReactFlow
                nodes={memoizedNodes}
                edges={memoizedEdges}
                onConnect={onConnect}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
                onInit={(instance) => instance.fitView(defaultFitViewOptions)}
                minZoom={MIN_ZOOM}
                maxZoom={MAX_ZOOM}
                zoomOnPinch
                zoomOnDoubleClick
                connectionLineType={ConnectionLineType.SmoothStep}
                fitViewOptions={defaultFitViewOptions}
                className={styles.nodeEditor}
                nodeTypes={nodeTypes}
                edgeTypes={edgeTypes}
                elevateNodesOnSelect
                nodesFocusable
                attributionPosition={'bottom-left'}
                {...editorProps}
            >
                <Background />
                <Controls
                    position={'top-right'}
                    showInteractive={false}
                    fitViewOptions={{ ...defaultFitViewOptions, duration: 500 }}
                />
            </ReactFlow>
            {debug && (
                <>
                    <Typography.Text strong>{t('Nodes')}</Typography.Text>
                    {nodes.map((node) => (
                        <div key={node.id}>
                            Node {node.id} - x: {node.position.x.toFixed(2)}, y: {node.position.y.toFixed(2)}
                        </div>
                    ))}
                </>
            )}
        </>
    );
}
