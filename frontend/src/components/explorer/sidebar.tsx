import { useCallback } from 'react';
import { Node, useReactFlow, useStore } from '@xyflow/react';
import { Select } from 'antd';
import styles from './sidebar.module.scss';

// const transformSelector = (state: any) => state.transform;

export default ({ nodes, setNodes }: { nodes: Node[]; setNodes: (nodes: Node[] | ((nodes: Node[]) => Node[])) => void }) => {
    // const transform = useStore(transformSelector);
    const { setCenter, getNode } = useReactFlow();

    const selectNode = useCallback(
        (nodeId: string) => {
            setNodes((nodes: Node[]) =>
                nodes.map((node) => {
                    const isSelected: boolean = node.id === nodeId;
                    console.log('isSelected', isSelected);
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            isMainNode: isSelected,
                        },
                        selected: isSelected,
                    };
                }),
            );
            const nodeToFocus = getNode(nodeId);
            if (nodeToFocus) {
                setCenter(nodeToFocus.position.x, nodeToFocus.position.y, {
                    zoom: 1.2, // adjust as needed
                    duration: 800,
                });
            }
        },
        [getNode, setCenter, setNodes],
    );

    return (
        <aside className={styles.aside}>
            <Select
                showSearch
                placeholder="Select a node"
                onSelect={(value: string) => {
                    selectNode(value);
                }}
                filterOption={(input: string, option?: { value: string; label: string }) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                style={{ width: '20em', margin: '1em' }} // TODO: was unsucessful in using scss
            >
                {nodes.map((node) => (
                    <Select.Option label={node.data.name} value={node.data.id}>
                        <>{node.data.name}</>
                    </Select.Option>
                ))}
            </Select>
        </aside>
    );
};
