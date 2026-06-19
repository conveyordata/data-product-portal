import { type Node, useReactFlow } from '@xyflow/react';
import { Flex, Select, Switch, Tooltip } from 'antd';
import { type MouseEvent, useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { ExplorerNodeTypes } from '@/components/charts/node-editor/node-types.ts';
import type { GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
import { defaultFitViewOptions } from '../../charts/node-editor/node-editor';
import { NodeContext } from './node-context';
import styles from './sidebar.module.scss';

export type SidebarFilters = {
    explorationsEnabled: boolean;
    outputPortsEnabled: boolean;
    domainsEnabled: boolean;
};

type Props = {
    nodes: Node[];
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

        const data = node.data as Record<string, GetDataProductResponse>;

        return {
            name: String(data.name || ''),
            domain: String(data.domain || ''),
            description: String(data.description || ''),
        };
    }

    const groupedNodes = useMemo(() => {
        const groups = {
            Domains: nodes.filter((node) => node.type === ExplorerNodeTypes.DomainNode),
            'Data Products': nodes.filter((node) => node.type === ExplorerNodeTypes.DataProductNode),
            'Output Ports': nodes.filter((node) => node.type === ExplorerNodeTypes.OutputPortNode),
            'Technical Assets': nodes.filter((node) => node.type === ExplorerNodeTypes.TechnicalAssetNode),
            Explorations: nodes.filter((node) => node.type === ExplorerNodeTypes.ExplorationNode),
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
                case 'Explorations':
                    return t('Explorations');
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
            <Tooltip title={t('Group all nodes in their own domain')}>
                <Flex align="center" gap="small">
                    <Switch
                        checked={sidebarFilters.domainsEnabled}
                        onChange={(checked) => onFilterChange({ ...sidebarFilters, domainsEnabled: checked })}
                        size="small"
                    />
                    {t('Group by Domain')}
                </Flex>
            </Tooltip>
            <Tooltip title={t('Show Explorations in the explorer')}>
                <Flex align="center" gap="small">
                    <Switch
                        checked={sidebarFilters.explorationsEnabled}
                        onChange={(checked) => onFilterChange({ ...sidebarFilters, explorationsEnabled: checked })}
                        size="small"
                    />
                    {t('Show Explorations')}
                </Flex>
            </Tooltip>
            <Tooltip
                title={t(
                    'Shows Output Ports in the explorer, when this is disabled Output Ports are abstracted as direct connections between Data Products and/or Explorations',
                )}
            >
                <Flex align="center" gap="small">
                    <Switch
                        checked={sidebarFilters.outputPortsEnabled}
                        onChange={(checked) => onFilterChange({ ...sidebarFilters, outputPortsEnabled: checked })}
                        size="small"
                    />
                    {t('Show Output Ports')}
                </Flex>
            </Tooltip>
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
