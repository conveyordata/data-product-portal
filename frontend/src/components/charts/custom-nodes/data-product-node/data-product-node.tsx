import type { Node, NodeProps, Position } from '@xyflow/react';
import type { ReactNode } from 'react';

import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import type { DataProductIcon } from '@/types/data-product-type';
import { DataProductRoleAssignmentContract } from '@/types/roles/role.contract';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';

export type DataProductNodeProps = Node<{
    id: string;
    name: string;
    icon_key: DataProductIcon;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    domain?: string;
    assignments?: Array<DataProductRoleAssignmentContract>;
    description?: string;
    onClick?: () => void;
}>;

export function DataProductNode({
    data: {
        name,
        id,
        icon_key,
        isMainNode,
        nodeToolbarActions,
        targetHandlePosition,
        sourceHandlePosition,
        isActive,
        domain,
        assignments,
        description,
        onClick,
    },
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
                    domain,
                    assignments,
                    description,
                    onClick,
                }}
                {...props}
            />
        </>
    );
}
