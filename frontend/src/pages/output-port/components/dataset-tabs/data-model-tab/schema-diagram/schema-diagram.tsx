import '@xyflow/react/dist/style.css';

import type { Edge, Node, NodeChange } from '@xyflow/react';
import { applyNodeChanges, Background, Controls, ReactFlow, ReactFlowProvider } from '@xyflow/react';
import { Flex, Popover, Space, Splitter, Table, Tabs, Tag, Typography } from 'antd';
import type { TFunction } from 'i18next';
import type { MouseEvent } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type {
    SchemaObjectResponse,
    SchemaPropertyResponse,
    SchemaRelationshipResponse,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { inferRelationships } from './infer-relationships.ts';
import { SCHEMA_OBJECT_NODE_TYPE, SchemaObjectNode, type SchemaObjectNodeData } from './schema-object-node.tsx';

const { Text } = Typography;

const nodeTypes = { [SCHEMA_OBJECT_NODE_TYPE]: SchemaObjectNode };

const NODE_WIDTH = 260;
const ROW_HEIGHT = 28;
const HEADER_HEIGHT = 37;
const COLUMN_GAP = 80;
const ROW_GAP = 60;
const COLUMNS = 3;

function getPropertyColumns(t: TFunction) {
    return [
        {
            title: t('Name'),
            key: 'name',
            render: (_: unknown, record: SchemaPropertyResponse) => (
                <Space orientation="vertical" size={0}>
                    <Text strong>{record.name}</Text>
                    {record.business_name && <Text type="secondary">{record.business_name}</Text>}
                </Space>
            ),
        },
        {
            title: t('Type'),
            key: 'type',
            render: (_: unknown, record: SchemaPropertyResponse) =>
                record.logical_type ? <Text type="secondary">{record.logical_type}</Text> : null,
        },
        {
            title: t('Required'),
            key: 'required',
            render: (_: unknown, record: SchemaPropertyResponse) => (
                <Text type="secondary">{record.required ? t('Yes') : t('No')}</Text>
            ),
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            key: 'description',
            render: (description: string | null) => (description ? <Text>{description}</Text> : null),
        },
        {
            title: t('Example'),
            key: 'example',
            render: (_: unknown, record: SchemaPropertyResponse) => {
                const example = record.examples?.[0];
                return example ? (
                    <Text type="secondary" code>
                        {String(example)}
                    </Text>
                ) : null;
            },
        },
        {
            title: t('Flags'),
            key: 'flags',
            render: (_: unknown, record: SchemaPropertyResponse) => (
                <Space size={8}>
                    {record.primary_key && (
                        <Text type="warning" strong>
                            {t('PK')}
                        </Text>
                    )}
                    {record.unique && (
                        <Text type="success" strong>
                            {t('Unique')}
                        </Text>
                    )}
                    {record.partitioned && (
                        <Text type="danger" strong>
                            {t('Partitioned')}
                        </Text>
                    )}
                </Space>
            ),
        },
    ];
}

type EdgePopoverState = {
    x: number;
    y: number;
    sourceLabel: string;
    targetLabel: string;
    cardinality: string;
};

type Props = {
    schemaObjects: SchemaObjectResponse[];
    declaredRelationships?: SchemaRelationshipResponse[];
    onSelectObject?: (id: string) => void;
};

export function SchemaDiagram({ schemaObjects, declaredRelationships, onSelectObject }: Props) {
    const { t } = useTranslation();
    const [nodes, setNodes] = useState<Node<SchemaObjectNodeData>[]>([]);
    const [edgePopover, setEdgePopover] = useState<EdgePopoverState | null>(null);
    const [highlightedPropertyIds, setHighlightedPropertyIds] = useState<Set<string>>(new Set());

    // Prefer relationships the producer declared in the contract; fall back to the name-matching heuristic.
    const relationships = useMemo(() => {
        if (declaredRelationships && declaredRelationships.length > 0) {
            return declaredRelationships.map((relationship) => ({
                id: relationship.id,
                sourceObjectId: relationship.source_object_id,
                sourcePropertyId: relationship.source_property_id,
                targetObjectId: relationship.target_object_id,
                targetPropertyId: relationship.target_property_id,
            }));
        }
        return inferRelationships(schemaObjects);
    }, [schemaObjects, declaredRelationships]);

    const objectById = useMemo(() => new Map(schemaObjects.map((object) => [object.id, object])), [schemaObjects]);

    const propertyById = useMemo(() => {
        const map = new Map<string, SchemaPropertyResponse>();
        for (const object of schemaObjects) {
            for (const property of object.properties ?? []) {
                map.set(property.id, property);
            }
        }
        return map;
    }, [schemaObjects]);

    const fkPropertyIdsByObject = useMemo(() => {
        const map = new Map<string, Set<string>>();
        for (const relationship of relationships) {
            const set = map.get(relationship.sourceObjectId) ?? new Set<string>();
            set.add(relationship.sourcePropertyId);
            map.set(relationship.sourceObjectId, set);
        }
        return map;
    }, [relationships]);

    // Preserve dragged position / selection across schema refetches instead of resetting the layout.
    useEffect(() => {
        setNodes((previousNodes) => {
            const previousPositions = new Map(previousNodes.map((node) => [node.id, node.position]));
            const previousSelection = new Map(previousNodes.map((node) => [node.id, node.selected ?? false]));
            const columnY = new Array(COLUMNS).fill(0);
            return schemaObjects.map((schemaObject, index) => {
                const column = index % COLUMNS;
                const height = HEADER_HEIGHT + (schemaObject.properties?.length ?? 0) * ROW_HEIGHT;
                const fallbackPosition = { x: column * (NODE_WIDTH + COLUMN_GAP), y: columnY[column] };
                columnY[column] += height + ROW_GAP;
                return {
                    id: schemaObject.id,
                    type: SCHEMA_OBJECT_NODE_TYPE,
                    position: previousPositions.get(schemaObject.id) ?? fallbackPosition,
                    selected: previousSelection.get(schemaObject.id) ?? index === 0,
                    data: {
                        name: schemaObject.name,
                        physicalType: schemaObject.physical_type,
                        properties: schemaObject.properties ?? [],
                        fkPropertyIds: fkPropertyIdsByObject.get(schemaObject.id) ?? new Set<string>(),
                        highlightedPropertyIds: new Set<string>(),
                    },
                };
            });
        });
    }, [schemaObjects, fkPropertyIdsByObject]);

    const onNodesChange = useCallback(
        (changes: NodeChange<Node<SchemaObjectNodeData>>[]) => {
            setNodes((currentNodes) => applyNodeChanges(changes, currentNodes));
            const selectionChange = changes.find((change) => change.type === 'select' && change.selected);
            if (selectionChange?.type === 'select') {
                onSelectObject?.(selectionChange.id);
            }
        },
        [onSelectObject],
    );

    const renderedNodes = useMemo(
        () => nodes.map((node) => ({ ...node, data: { ...node.data, highlightedPropertyIds } })),
        [nodes, highlightedPropertyIds],
    );

    const selectObjectFromTab = (id: string) => {
        setNodes((currentNodes) => currentNodes.map((node) => ({ ...node, selected: node.id === id })));
        onSelectObject?.(id);
    };

    const edges: Edge[] = useMemo(
        () =>
            relationships.map((relationship) => ({
                id: relationship.id,
                source: relationship.sourceObjectId,
                sourceHandle: `${relationship.sourcePropertyId}-source`,
                target: relationship.targetObjectId,
                targetHandle: `${relationship.targetPropertyId}-target`,
            })),
        [relationships],
    );

    const onEdgeClick = useCallback(
        (event: MouseEvent, edge: Edge) => {
            const relationship = relationships.find((r) => r.id === edge.id);
            if (!relationship) return;
            const sourceObject = objectById.get(relationship.sourceObjectId);
            const sourceProperty = propertyById.get(relationship.sourcePropertyId);
            const targetObject = objectById.get(relationship.targetObjectId);
            const targetProperty = propertyById.get(relationship.targetPropertyId);
            setEdgePopover({
                x: event.clientX,
                y: event.clientY,
                sourceLabel: `${sourceObject?.name}.${sourceProperty?.name}`,
                targetLabel: `${targetObject?.name}.${targetProperty?.name}`,
                cardinality: sourceProperty?.unique ? t('One-to-one') : t('Many-to-one'),
            });
            setHighlightedPropertyIds(new Set([relationship.sourcePropertyId, relationship.targetPropertyId]));
        },
        [relationships, objectById, propertyById, t],
    );

    const selectedObjectId = nodes.find((node) => node.selected)?.id;

    const tabItems = schemaObjects.map((schema) => ({
        key: schema.id,
        label: schema.name,
        children: (
            <Flex vertical gap="small">
                {(schema?.physical_type ||
                    (schema?.physical_name && schema?.physical_name !== schema.name) ||
                    schema?.description) && (
                    <Space size="small">
                        {schema.physical_type && <Tag>{schema.physical_type}</Tag>}
                        {schema.physical_name && schema.physical_name !== schema.name && (
                            <Tag>{schema.physical_name}</Tag>
                        )}
                        {schema.description && <Text type="secondary">{schema.description}</Text>}
                    </Space>
                )}
                <Table<SchemaPropertyResponse>
                    dataSource={schema?.properties ?? []}
                    columns={getPropertyColumns(t)}
                    rowKey="id"
                    size="small"
                    pagination={false}
                    scroll={{ x: 'max-content' }}
                    expandable={{ childrenColumnName: 'properties' }}
                    locale={{ emptyText: t('No properties defined') }}
                />
            </Flex>
        ),
    }));

    return (
        <Splitter style={{ height: 640 }}>
            <Splitter.Panel defaultSize="55%" min="30%" collapsible>
                <ReactFlowProvider>
                    <ReactFlow
                        nodes={renderedNodes}
                        edges={edges}
                        nodeTypes={nodeTypes}
                        onNodesChange={onNodesChange}
                        onEdgeClick={onEdgeClick}
                        onPaneClick={() => {
                            setEdgePopover(null);
                            setHighlightedPropertyIds(new Set());
                        }}
                        onMoveStart={() => {
                            setEdgePopover(null);
                            setHighlightedPropertyIds(new Set());
                        }}
                        fitView
                        minZoom={0.1}
                        maxZoom={2}
                        proOptions={{ hideAttribution: true }}
                        nodesConnectable={false}
                    >
                        <Background />
                        <Controls position="top-right" showInteractive={false} />
                    </ReactFlow>
                    {edgePopover && (
                        <Popover
                            open
                            onOpenChange={(open) => !open && setEdgePopover(null)}
                            content={
                                <Space orientation="vertical" size={0}>
                                    <Text strong>
                                        {edgePopover.sourceLabel} → {edgePopover.targetLabel}
                                    </Text>
                                    <Text type="secondary">{edgePopover.cardinality}</Text>
                                </Space>
                            }
                        >
                            <div
                                style={{
                                    position: 'fixed',
                                    left: edgePopover.x,
                                    top: edgePopover.y,
                                    width: 0,
                                    height: 0,
                                }}
                            />
                        </Popover>
                    )}
                </ReactFlowProvider>
            </Splitter.Panel>
            <Splitter.Panel defaultSize="45%" min="30%" collapsible>
                <div style={{ paddingLeft: 12 }}>
                    <Tabs activeKey={selectedObjectId} items={tabItems} onChange={selectObjectFromTab} />
                </div>
            </Splitter.Panel>
        </Splitter>
    );
}
