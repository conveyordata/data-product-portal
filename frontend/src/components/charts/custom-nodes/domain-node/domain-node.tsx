import type { Node, NodeProps } from '@xyflow/react';
import { NodeToolbar, Position } from '@xyflow/react';
import { Flex, Typography } from 'antd';
import type { ReactNode } from 'react';

import styles from '@/components/charts/custom-nodes/domain-node/domain-node.module.scss';

// Domain nodes are not BaseNodes because they don't have icons
export type DomainNodeProps = Node<{
    id: string;
    name: string;
    borderType?: 'square' | 'round';
    nodeToolbarActions?: ReactNode;
    targetHandlePosition?: Position;
    sourceHandlePosition?: Position;
    isActive?: boolean;
    onClick?: () => void;
    backgroundColor: string;
    borderColor: string;
}>;

export function DomainNode<T extends DomainNodeProps>(nodeProps: NodeProps<T>) {
    const { data, width, height } = nodeProps;
    const { onClick, nodeToolbarActions, name, backgroundColor, borderColor } = data;
    return (
        <>
            <Typography.Paragraph ellipsis={{ tooltip: name, rows: 2 }} className={styles.nodeLabel}>
                {name}
            </Typography.Paragraph>
            <Flex className={styles.nodeContainer} onClick={onClick}>
                <Flex className={styles.nodeWrapper}>
                    <div
                        className={styles.nodeBox}
                        // override styles.nodeBox on the parts that need to be dynamic
                        style={{
                            backgroundColor: backgroundColor, // although there is a default color specified in domain-node.module.scss
                            borderColor: borderColor, // although there is a default color in domain-node.module.scss
                            height: height,
                            width: width,
                            visibility: 'visible',
                            borderRadius: '8px',
                        }}
                    >
                    </div>
                </Flex>
                {nodeToolbarActions && <NodeToolbar position={Position.Bottom}>{nodeToolbarActions}</NodeToolbar>}
            </Flex>
        </>
    );
}
