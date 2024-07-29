import { NodeProps, Position } from 'reactflow';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import { ReactNode } from 'react';
import { getDataOutputIcon } from '@/utils/data-output-type-icon.helper';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';

export type DataOutputNodeProps = {
    id: string;
    name: string;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    icon: string;
};

export function DataOutputNode({
    data: { name, id, isMainNode, nodeToolbarActions, targetHandlePosition, sourceHandlePosition, icon, isActive },
    ...props
}: NodeProps<DataOutputNodeProps>) {
    return (
        <>
            <BaseNode
                data={{
                    isMainNode,
                    name,
                    id,
                    icon: getDataOutputIcon(icon),
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
