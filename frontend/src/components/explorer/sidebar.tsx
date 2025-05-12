import { Node, useReactFlow } from '@xyflow/react';
import { Checkbox, Select } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

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

        const data = node.data as Record<string, any>;
        console.log(node);

        return {
            name: String(data.name || ''),
            domain: String(data.domain || ''),
            members: Array.isArray(data.members) ? data.members : [],
            description: String(data.description || ''),
        };
    }

    return (
        <div className={styles.sidebarContainer}>
            <Checkbox
                checked={sidebarFilters.domainsEnabled}
                value="domain"
                className={styles.checkbox}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        domainsEnabled: e.target.checked,
                    });
                }}
            >
                {t('Domains')}
            </Checkbox>
            <Checkbox
                checked={sidebarFilters.dataProductsEnabled}
                value="data product"
                className={styles.checkbox}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        dataProductsEnabled: e.target.checked,
                    });
                }}
            >
                {t('Data Products')}
            </Checkbox>
            <Checkbox
                checked={sidebarFilters.datasetsEnabled}
                value="dataset"
                className={styles.checkbox}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        datasetsEnabled: e.target.checked,
                    });
                }}
            >
                {t('Datasets')}
            </Checkbox>
            <Checkbox
                checked={sidebarFilters.dataOutputsEnabled}
                value="data output"
                className={styles.checkbox}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        dataOutputsEnabled: e.target.checked,
                    });
                }}
            >
                {t('Data Outputs')}
            </Checkbox>
            <Select
                showSearch
                placeholder={String('Select a node')}
                onSelect={(value: string) => {
                    selectNode(value); // Update the selected node
                }}
                filterOption={(input: string, option?: { value: string; label: string }) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                className={styles.select}
            >
                {nodes.map((node) => (
                    <Select.Option key={node.id} label={node.data.name} value={node.id}>
                        {String(node.data.name)}
                    </Select.Option>
                ))}
            </Select>

            <div className={styles.p}>
                {nodeId && (
                    <div>
                        Name: {getNodeDataForSideBar(nodeId)?.name}
                        <br />
                        Domain: {getNodeDataForSideBar(nodeId)?.domain}
                        <br />
                        Members: <br />
                        <ul>
                            {getNodeDataForSideBar(nodeId)?.members?.map((member: string) => (
                                <li key={member}>
                                    {member}
                                    <br />
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
