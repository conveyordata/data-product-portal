import type { Node, NodeProps, Position } from '@xyflow/react';
import type { ReactNode } from 'react';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';

type DatasetNodeProps = Node<{
    id: string;
    name: string;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    domain?: string;
    centeredHandles?: boolean;
    onClick: () => void;
}>;

export function DatasetNode({
    data: {
        name,
        id,
        isMainNode,
        nodeToolbarActions,
        targetHandlePosition,
        sourceHandlePosition,
        isActive,
        domain,
        centeredHandles,
        onClick,
    },
    ...props
}: NodeProps<DatasetNodeProps>) {
    return (
        <BaseNode
            data={{
                isMainNode,
                name,
                id,
                icon: datasetBorderIcon,
                borderType: 'square',
                nodeToolbarActions,
                targetHandlePosition,
                sourceHandlePosition,
                isActive,
                domain,
                centeredHandles,
                onClick,
            }}
            {...props}
        />
    );
}
