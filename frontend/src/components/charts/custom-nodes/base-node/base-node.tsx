import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import type { Node, NodeProps } from '@xyflow/react';
import { NodeToolbar, Position } from '@xyflow/react';
import { Flex, Typography } from 'antd';
import type { ComponentType, ForwardRefExoticComponent, ReactNode, SVGProps } from 'react';

import { DefaultHandle } from '@/components/charts/custom-handles/default-handle.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';

import styles from './base-node.module.scss';

export type BaseNodeProps = Node<{
    id: string;
    name: string;
    icon:
        | ComponentType<CustomIconComponentProps | SVGProps<SVGSVGElement>>
        | ForwardRefExoticComponent<CustomIconComponentProps>;
    borderType?: 'square' | 'round';
    isMainNode?: boolean;
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
}>;

export function BaseNode<T extends BaseNodeProps>({
    data: { name, isMainNode, icon, borderType = 'round', nodeToolbarActions, isActive = true },
}: NodeProps<T>) {
    return (
        <>
            <Flex className={styles.nodeContainer}>
                <DefaultHandle id={'left_t'} type={'target'} position={Position.Left} isConnectable={false} />
                <DefaultHandle id={'left_s'} type={'source'} position={Position.Left} isConnectable={false} />
                <Flex className={styles.nodeWrapper}>
                    <CustomSvgIconLoader
                        iconComponent={icon}
                        hasRoundBorder={borderType === 'round'}
                        hasSquareBorder={borderType === 'square'}
                        size={'large'}
                        inverted={isMainNode}
                        color={isActive ? 'primary' : 'light'}
                    />
                </Flex>
                <DefaultHandle id={'right_t'} type={'target'} position={Position.Right} isConnectable={false} />
                <DefaultHandle id={'right_s'} type={'source'} position={Position.Right} isConnectable={false} />
                {nodeToolbarActions && <NodeToolbar position={Position.Bottom}>{nodeToolbarActions}</NodeToolbar>}
            </Flex>
            <Typography.Paragraph ellipsis={{ tooltip: name, rows: 2 }} className={styles.nodeLabel}>
                {name}
            </Typography.Paragraph>
        </>
    );
}
