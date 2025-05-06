import type { Node, NodeProps, Position } from '@xyflow/react';
import type { ReactNode } from 'react';

import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';

export type DataOutputNodeProps = Node<{
    id: string;
    name: string;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    icon_key: string;
    domain?: string;
}>;

export function DataOutputNode({
    data: {
        name,
        id,
        isMainNode,
        nodeToolbarActions,
        targetHandlePosition,
        sourceHandlePosition,
        icon_key,
        isActive,
        domain,
    },
    ...props
}: NodeProps<DataOutputNodeProps>) {
    return (
        <>
            <BaseNode
                data={{
                    isMainNode,
                    name,
                    id,
                    icon: getDataOutputIcon(icon_key)!,
                    borderType: 'square',
                    nodeToolbarActions,
                    targetHandlePosition,
                    sourceHandlePosition,
                    isActive,
                    domain,
                }}
                {...props}
            />
        </>
    );
}
