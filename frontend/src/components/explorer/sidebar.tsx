import { Node, useReactFlow } from '@xyflow/react';
import { Select, Tag } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductContract } from '@/types/data-product';

import { NodeContext } from './node-context';
import styles from './sidebar.module.scss';

export type SidebarFilters = {
    dataProductsEnabled: boolean;
    datasetsEnabled: boolean;
    dataOutputsEnabled: boolean;
    domainsEnabled: boolean;
};

export function Sidebar({
    nodes,
    sidebarFilters,
    onFilterChange,
}: {
    nodes: Node[];
    setNodes: (nodes: Node[] | ((nodes: Node[]) => Node[])) => void;
    sidebarFilters: SidebarFilters;
    onFilterChange: (filters: SidebarFilters) => void;
}) {
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

    function getNodeDataForSideBar(nodeId: string) {
        const node = getNode(nodeId);
        if (!node) return null;

        const data = node.data as Record<string, DataProductContract>;

        return {
            name: String(data.name || ''),
            domain: String(data.domain || ''),
            assignments: Array.isArray(data.assignments) ? data.assignments : [],
            description: String(data.description || ''),
        };
    }

    return (
        <div className={styles.sidebarContainer}>
            {/* <Tag.CheckableTag
                checked={sidebarFilters.domainsEnabled}
                className={styles.checkableTag}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        domainsEnabled: e.valueOf(),
                    });
                }}
            >
                {t('Domains')}
            </Tag.CheckableTag> */}
            <Tag.CheckableTag
                checked={sidebarFilters.dataProductsEnabled}
                className={styles.checkableTag}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        dataProductsEnabled: e.valueOf(),
                    });
                }}
            >
                {t('Data Products')}
            </Tag.CheckableTag>
            <Tag.CheckableTag
                checked={sidebarFilters.datasetsEnabled}
                className={styles.checkableTag}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        datasetsEnabled: e.valueOf(),
                    });
                }}
            >
                {t('Datasets')}
            </Tag.CheckableTag>
            <Tag.CheckableTag
                checked={sidebarFilters.dataOutputsEnabled}
                className={styles.checkableTag}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        dataOutputsEnabled: e.valueOf(),
                    });
                }}
            >
                {t('Data Outputs')}
            </Tag.CheckableTag>
            <Select
                className={styles.select}
                showSearch
                placeholder={String('Select a node')}
                onSelect={(value: string) => {
                    selectNode(value); // Update the selected node
                }}
                filterOption={(input: string, option?: { value: string; label: string }) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
            >
                {nodes.map((node) => (
                    <Select.Option key={node.id} label={node.data.name} value={node.id}>
                        {String(node.data.name)}
                    </Select.Option>
                ))}
            </Select>
            <NodeContext className={styles.p} nodeId={nodeId} getNodeDataForSideBar={getNodeDataForSideBar} />
        </div>
    );
}
