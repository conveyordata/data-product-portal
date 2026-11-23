import '@xyflow/react/dist/style.css';

import type {
    Connection,
    Edge,
    FitViewOptions,
    Node,
    OnEdgesChange,
    OnNodesChange,
    ReactFlowProps,
} from '@xyflow/react';
import { Background, ConnectionLineType, Controls, ReactFlow } from '@xyflow/react';

import { edgeTypes, nodeTypes } from '@/components/charts/node-editor/node-types.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import styles from './node-editor.module.scss';

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 2;

export const defaultFitViewOptions: FitViewOptions = {
    maxZoom: 1.25,
    duration: 650,
};

type Props = {
    nodes: Node[];
    edges: Edge[];
    onConnect: (connection: Connection) => void;
    onNodesChange: OnNodesChange;
    onEdgesChange: OnEdgesChange;
    onNodeClick?: ReactFlowProps['onNodeClick'];
    onPaneClick?: ReactFlowProps['onPaneClick'];
    editorProps?: Omit<ReactFlowProps, 'nodes' | 'edges' | 'onConnect' | 'onNodesChange' | 'onEdgesChange'>;
    debug?: boolean;
    isLoading?: boolean;
};

export function NodeEditor({
    nodes = [],
    edges = [],
    onConnect,
    onNodesChange,
    onEdgesChange,
    onNodeClick,
    onPaneClick,
    editorProps,
    isLoading,
}: Props) {
    if (isLoading) {
        return <LoadingSpinner />;
    }
    return (
        <ReactFlow
            nodes={nodes}
            edges={edges}
            onConnect={onConnect}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            fitView
            forceColorMode="light"
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
            attributionPosition="bottom-left"
            {...editorProps}
        >
            <Background />
            <Controls position="top-right" showInteractive={false} fitViewOptions={defaultFitViewOptions} />
        </ReactFlow>
    );
}
