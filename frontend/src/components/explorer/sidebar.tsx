import { Node, useReactFlow } from '@xyflow/react';
import { Select } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import styles from './sidebar.module.scss';

export function Sidebar({ nodes }: { nodes: Node[]; setNodes: (nodes: Node[] | ((nodes: Node[]) => Node[])) => void }) {
    const { setCenter, getNode, setNodes } = useReactFlow();
    const [nodeId, setNodeId] = useState<string | null>(null);
    const { t } = useTranslation();
    const selectNode = useCallback(
        (nodeId: string) => {
            setNodes((nodes: Node[]) =>
                nodes.map((node) => ({
                    ...node,
                    data: {
                        ...node.data,
                        isMainNode: node.id === nodeId, // Mark as the main node (invert SVG colors)
                    },
                    selected: node.id === nodeId, // Mark as selected (show tooltip with link)
                })),
            );
            setNodeId(nodeId);
        },
        [setNodes],
    );

    useEffect(() => {
        if (!nodeId) return;

        // Give React Flow time to update its internals
        const timeout = setTimeout(() => {
            const nodeToFocus = getNode(nodeId);
            if (nodeToFocus) {
                setCenter(nodeToFocus.position.x, nodeToFocus.position.y, {
                    zoom: 1.2,
                    duration: 800,
                });
            }
        }, 50); // 50ms is usually enough

        return () => clearTimeout(timeout);
    }, [nodeId, getNode, setCenter]);

    return (
        <Select
            showSearch
            placeholder={t('Select a node')}
            onSelect={(value: string) => {
                selectNode(value); // Update the selected node
            }}
            filterOption={(input: string, option?: { value: string; label: string }) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            className={styles.sidebar}
        >
            {nodes.map((node) => (
                <Select.Option key={node.id} label={node.data.name} value={node.id}>
                    {String(node.data.name)}
                </Select.Option>
            ))}
        </Select>
    );
}
