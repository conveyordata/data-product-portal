import { NodeProps, NodeToolbar, Position } from 'reactflow';
import styles from './base-node.module.scss';
import { Flex, Typography } from 'antd';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { DefaultHandle } from '@/components/charts/custom-handles/default-handle.tsx';
import { ComponentType, ForwardRefExoticComponent, ReactNode, SVGProps } from 'react';
import { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';

export type BaseNodeProps = {
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
};

export function BaseNode<T extends BaseNodeProps>({
    data: {
        name,
        isMainNode,
        icon,
        borderType = 'round',
        nodeToolbarActions,
        targetHandlePosition = Position.Left,
        sourceHandlePosition = Position.Right,
        isActive = true,
    },
}: NodeProps<T>) {
    return (
        <>
            <Flex className={styles.nodeContainer}>
                <DefaultHandle id={'left_t'} type={'target'} position={Position.Left} isConnectable={false} />
                <DefaultHandle id={'left_s'} type={'source'} position={Position.Left} isConnectable={false} />
                <Flex className={styles.nodeWrapper}>
                    <Flex>
                        <CustomSvgIconLoader
                            iconComponent={icon}
                            hasRoundBorder={borderType === 'round'}
                            hasSquareBorder={borderType === 'square'}
                            size={'large'}
                            inverted={isMainNode}
                            color={isActive ? 'primary' : 'light'}
                        />
                    </Flex>
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
