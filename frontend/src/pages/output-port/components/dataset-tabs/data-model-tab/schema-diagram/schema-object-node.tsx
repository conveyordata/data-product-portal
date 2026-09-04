import { KeyOutlined, LinkOutlined } from '@ant-design/icons';
import type { Node, NodeProps } from '@xyflow/react';
import { Position } from '@xyflow/react';
import { Card, Flex, Space, Tag, Typography } from 'antd';
import { createContext, memo, useContext } from 'react';
import { DefaultHandle } from '@/components/charts/custom-handles/default-handle.tsx';
import type { SchemaPropertyResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

const { Text } = Typography;

export const SCHEMA_OBJECT_NODE_TYPE = 'schemaObjectNode';
export const SCHEMA_OBJECT_NODE_WIDTH = 280;
export const SCHEMA_OBJECT_ROW_HEIGHT = 28;
export const EMPTY_PROPERTY_IDS: ReadonlySet<string> = new Set();

// Stable callback references, provided via context so hovering/clicking a row never forces every other node to re-render.
export const PropertyHoverContext = createContext<(propertyId: string | null) => void>(() => undefined);
export const PropertyClickContext = createContext<(propertyId: string) => void>(() => undefined);

export type SchemaObjectNodeData = {
    name: string;
    physicalType?: string | null;
    properties: SchemaPropertyResponse[];
    fkPropertyIds: Set<string>;
    highlightedPropertyIds: ReadonlySet<string>;
};

type SchemaObjectNodeType = Node<SchemaObjectNodeData>;

function SchemaObjectNodeComponent({ data, selected }: NodeProps<SchemaObjectNodeType>) {
    const { name, physicalType, properties, fkPropertyIds, highlightedPropertyIds } = data;
    const onPropertyHover = useContext(PropertyHoverContext);
    const onPropertyClick = useContext(PropertyClickContext);

    return (
        <Card
            size="small"
            title={name}
            extra={physicalType && <Tag>{physicalType}</Tag>}
            style={{ width: SCHEMA_OBJECT_NODE_WIDTH, borderColor: selected ? 'var(--ant-color-primary)' : undefined }}
            styles={{ body: { padding: 0 } }}
        >
            {properties.map((property) => (
                <Flex
                    key={property.id}
                    justify="space-between"
                    align="center"
                    gap="small"
                    onMouseEnter={() => onPropertyHover(property.id)}
                    onMouseLeave={() => onPropertyHover(null)}
                    onClick={() => onPropertyClick(property.id)}
                    style={{
                        position: 'relative',
                        height: SCHEMA_OBJECT_ROW_HEIGHT,
                        padding: '0 12px',
                        cursor: 'pointer',
                        backgroundColor: highlightedPropertyIds.has(property.id)
                            ? 'var(--ant-color-primary-bg)'
                            : undefined,
                    }}
                >
                    <DefaultHandle id={`${property.id}-target`} type="target" position={Position.Left} />
                    <Space size={6}>
                        {property.primary_key ? (
                            <KeyOutlined />
                        ) : fkPropertyIds.has(property.id) ? (
                            <LinkOutlined />
                        ) : (
                            <Text> </Text>
                        )}
                        <Text strong={property.primary_key}>{property.name}</Text>
                    </Space>
                    <Text type="secondary">{property.logical_type}</Text>
                    <DefaultHandle id={`${property.id}-source`} type="source" position={Position.Right} />
                </Flex>
            ))}
        </Card>
    );
}

export const SchemaObjectNode = memo(SchemaObjectNodeComponent);
