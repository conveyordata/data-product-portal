import { type Node, useReactFlow } from '@xyflow/react';
import { Flex, Segmented, Select } from 'antd';
import { type MouseEvent, useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { DataProductContract } from '@/types/data-product';
import { defaultFitViewOptions } from '../../charts/node-editor/node-editor';
import { CustomNodeTypes } from '../../charts/node-editor/node-types';
import { NodeContext } from './node-context';
import styles from './sidebar.module.scss';

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
        <Flex className={styles.sidebarContainer} vertical gap={'small'}>
            <Segmented
                className={styles.checkableTag}
                options={[
                    {
                        label: t('All'),
                        value: 'all',
                    },
                    {
                        label: t('Data Products'),
                        value: 'dataProducts',
                    },
                    {
                        label: t('Output Ports'),
                        value: 'outputPorts',
                    },
                ]}
                onChange={(value) => {
                    if (value === 'outputPorts') {
                        onFilterChange({
                            ...sidebarFilters,
                            dataProductsEnabled: false,
                            datasetsEnabled: true,
                        });
                    } else if (value === 'dataProducts') {
                        onFilterChange({
                            ...sidebarFilters,
                            dataProductsEnabled: true,
                            datasetsEnabled: false,
                        });
                    } else if (value === 'all') {
                        onFilterChange({
                            ...sidebarFilters,
                            dataProductsEnabled: true,
                            datasetsEnabled: true,
                        });
                    }
                }}
            />
            <Select
                placeholder={t('Select a node')}
                value={nodeId}
                showSearch={{
                    filterOption: (input: string, option?: { value: string; label: string }) =>
                        (option?.label ?? '').toLowerCase().includes(input.toLowerCase()),
                }}
                onSelect={(value: string) => {
                    nodeClick(undefined, { id: value } as Node);
                }}
                options={selectionOptions}
            />
            <NodeContext nodeId={nodeId} getNodeDataForSideBar={getNodeDataForSideBar} />
        </Flex>
    );
}
