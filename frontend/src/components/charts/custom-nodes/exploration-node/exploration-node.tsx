import type { Node, NodeProps, Position } from '@xyflow/react';
import type { ReactNode } from 'react';
import explorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';

type ExplorationNodeProps = Node<{
    id: string;
    name: string;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    domain?: string;
    description?: string;
    centeredHandles?: boolean;
    onClick?: () => void;
}>;

export function ExplorationNode({
    data: {
        name,
        id,
        isMainNode,
        nodeToolbarActions,
        targetHandlePosition,
        sourceHandlePosition,
        isActive,
        domain,
        description,
        centeredHandles,
        onClick,
    },
    ...props
}: NodeProps<ExplorationNodeProps>) {
    return (
        <BaseNode
            data={{
                name,
                id,
                isMainNode,
                icon: explorationBorderIcon,
                borderType: 'square',
                nodeToolbarActions,
                sourceHandlePosition,
                targetHandlePosition,
                isActive,
                domain,
                description,
                centeredHandles,
                onClick,
            }}
            {...props}
        />
    );
}
