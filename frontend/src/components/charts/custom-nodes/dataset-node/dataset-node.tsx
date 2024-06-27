import { NodeProps, Position } from 'reactflow';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import { ReactNode } from 'react';

export type DatasetNodeProps = {
    id: string;
    name: string;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
};

export function DatasetNode({
    data: { name, id, isMainNode, nodeToolbarActions, targetHandlePosition, sourceHandlePosition, isActive },
    ...props
}: NodeProps<DatasetNodeProps>) {
    return (
        <>
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
                }}
                {...props}
            />
        </>
    );
}
