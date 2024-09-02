import { NodeProps, Position } from 'reactflow';
import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import { ReactNode } from 'react';
import { getDataOutputIcon } from '@/utils/data-output-type-icon.helper';

export type DataOutputNodeProps = {
    id: string;
    name: string;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    icon_key: string;
};

export function DataOutputNode({
    data: { name, id, isMainNode, nodeToolbarActions, targetHandlePosition, sourceHandlePosition, icon_key, isActive },
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
                }}
                {...props}
            />
        </>
    );
}
