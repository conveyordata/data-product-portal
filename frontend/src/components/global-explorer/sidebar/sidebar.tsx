import { type Node, useReactFlow } from '@xyflow/react';
import { Select, Tag } from 'antd';
import { type MouseEvent, useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { DataProductContract } from '@/types/data-product';
import { defaultFitViewOptions } from '../../charts/node-editor/node-editor';
import { CustomNodeTypes } from '../../charts/node-editor/node-types';
import { NodeContext } from './node-context';
import styles from './sidebar.module.scss';

const { CheckableTag } = Tag;

export type SidebarFilters = {
    dataProductsEnabled: boolean;
    datasetsEnabled: boolean;
    domainsEnabled: boolean;
};

type Props = {
    nodes: Node[];
    setNodes: (nodes: Node[] | ((nodes: Node[]) => Node[])) => void;
    sidebarFilters: SidebarFilters;
    onFilterChange: (filters: SidebarFilters) => void;
    nodeId: string | null;
    nodeClick: (event: MouseEvent | undefined, node: Node) => void;
};

export function Sidebar({ nodes, sidebarFilters, onFilterChange, nodeId, nodeClick }: Props) {
    const { t } = useTranslation();
    const { getNode, setNodes, fitView } = useReactFlow();

    useEffect(() => {
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
    }, [nodeId, setNodes]);

    useEffect(() => {
        if (!nodeId) return;
        const timeout = setTimeout(async () => {
            await fitView({
                ...defaultFitViewOptions,
                nodes: [{ id: nodeId }],
            });
        }, 50);

        return () => clearTimeout(timeout);
    }, [nodeId, fitView]);

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

    const groupedNodes = useMemo(() => {
        const groups = {
            Domains: nodes.filter((node) => node.type === CustomNodeTypes.DomainNode),
            'Data Products': nodes.filter((node) => node.type === CustomNodeTypes.DataProductNode),
            'Output Ports': nodes.filter((node) => node.type === CustomNodeTypes.DatasetNode),
            'Technical Assets': nodes.filter((node) => node.type === CustomNodeTypes.DataOutputNode),
        };

        // Sort each group by name
        Object.values(groups).forEach((group) => {
            group.sort((a, b) => String(a.data.name || '').localeCompare(String(b.data.name || '')));
        });

        return groups;
    }, [nodes]);

    const translateGroupName = useCallback(
        (group: string) => {
            switch (group) {
                case 'Domains':
                    return t('Domains');
                case 'Data Products':
                    return t('Data Products');
                case 'Output Ports':
                    return t('Output Ports');
                case 'Technical Assets':
                    return t('Technical Assets');
                default:
                    return t('Undefined group');
            }
        },
        [t],
    );

    const selectionOptions = useMemo(
        () =>
            Object.entries(groupedNodes)
                .filter(([_, nodes]) => nodes.length > 0)
                .map(([groupName, nodes]) => ({
                    label: translateGroupName(groupName),
                    value: groupName,
                    options: nodes.map((node) => ({
                        label: node.data.name,
                        value: node.id,
                    })),
                })),
        [groupedNodes, translateGroupName],
    );

    return (
        <div className={styles.sidebarContainer}>
            <CheckableTag
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
            </CheckableTag>
            <CheckableTag
                checked={sidebarFilters.datasetsEnabled}
                className={styles.checkableTag}
                onChange={(e) => {
                    onFilterChange({
                        ...sidebarFilters,
                        datasetsEnabled: e.valueOf(),
                    });
                }}
            >
                {t('Output Ports')}
            </CheckableTag>
            <Select
                placeholder={t('Select a node')}
                value={nodeId}
                className={styles.select}
                showSearch={{
                    filterOption: (input: string, option?: { value: string; label: string }) =>
                        (option?.label ?? '').toLowerCase().includes(input.toLowerCase()),
                }}
                onSelect={(value: string) => {
                    nodeClick(undefined, { id: value } as Node);
                }}
                options={selectionOptions}
            />
            <NodeContext className={styles.p} nodeId={nodeId} getNodeDataForSideBar={getNodeDataForSideBar} />
        </div>
    );
}
