import type { Node, NodeProps, Position } from '@xyflow/react';
import type { ReactNode } from 'react';

import { BaseNode } from '@/components/charts/custom-nodes/base-node/base-node.tsx';
import type { DataProductIconKey } from '@/store/api/services/generated/configurationDataProductTypesApi.ts';
import type { DataProductRoleAssignment } from '@/types/roles';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';

type DataProductNodeProps = Node<{
    id: string;
    name: string;
    icon_key: DataProductIconKey;
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    domain?: string;
    assignments?: DataProductRoleAssignment[];
    description?: string;
    centeredHandles?: boolean;
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
        centeredHandles,
        onClick,
    },
    ...props
}: NodeProps<DataProductNodeProps>) {
    return (
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
                centeredHandles,
                onClick,
            }}
            {...props}
        />
    );
}
