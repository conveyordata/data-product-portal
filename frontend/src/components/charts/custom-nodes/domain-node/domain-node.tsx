import type { Node, NodeProps } from '@xyflow/react';
import { NodeToolbar, Position } from '@xyflow/react';
import { Flex, Typography } from 'antd';
import type { ReactNode } from 'react';

import { DefaultHandle } from '@/components/charts/custom-handles/default-handle.tsx';

import styles from '../base-node/base-node.module.scss';
// Domain nodes are not BaseNodes because they don't have icons

export type DomainNodeProps = Node<{
    id: string;
    name: string;
    borderType?: 'square' | 'round';
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
}>;

export function DomainNode<T extends DomainNodeProps>({ data: { name, nodeToolbarActions } }: NodeProps<T>) {
    return (
        <>
            <Flex className={styles.nodeContainer}>
                <DefaultHandle id={'left_t'} type={'target'} position={Position.Left} isConnectable={false} />
                <DefaultHandle id={'left_s'} type={'source'} position={Position.Left} isConnectable={false} />
                <Flex className={styles.nodeWrapper}>
                    <div
                        className={styles.nodeBox}
                        style={{
                            backgroundColor: 'rgba(255, 0, 255, 0.2)',
                            height: 150,
                            width: 270,
                            visibility: 'visible',
                            borderRadius: '8px',
                            //backgroundColor: isActive ? '#f0f0f0' : '#e0e0e0',
                        }}
                    >
                        <Typography.Text strong>Domain {name}</Typography.Text>
                    </div>
                </Flex>
                <DefaultHandle id={'right_t'} type={'target'} position={Position.Right} isConnectable={false} />
                <DefaultHandle id={'right_s'} type={'source'} position={Position.Right} isConnectable={false} />
                {nodeToolbarActions && <NodeToolbar position={Position.Bottom}>{nodeToolbarActions}</NodeToolbar>}
            </Flex>
            <Typography.Paragraph ellipsis={{ tooltip: name, rows: 2 }} className={styles.nodeLabel}>
                Domain {name}
            </Typography.Paragraph>
        </>
    );
}
