import { ReactNode } from 'react';
import { NodeProps, Position } from 'reactflow';

import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import { DataProductIcon } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';

export type DataProductNodeProps = {
    id: string;
    name: string;
    icon_key: DataProductIcon;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
};

export function DataProductNode({
    data: { name, id, icon_key, isMainNode, nodeToolbarActions, targetHandlePosition, sourceHandlePosition, isActive },
    ...props
}: NodeProps<DataProductNodeProps>) {
    return (
        <>
            <BaseNode
                data={{
                    name,
                    id,
                    isMainNode,
                    icon: getDataProductTypeIcon(icon_key),
                    nodeToolbarActions,
                    sourceHandlePosition,
                    targetHandlePosition,
                    isActive,
                }}
                {...props}
            />
        </>
    );
}
