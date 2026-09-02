import { KeyOutlined, LinkOutlined } from '@ant-design/icons';
import type { Node, NodeProps } from '@xyflow/react';
import { Position } from '@xyflow/react';
import { Card, Space, Table, Tag, Typography } from 'antd';
import { DefaultHandle } from '@/components/charts/custom-handles/default-handle.tsx';
import type { SchemaPropertyResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

const { Text } = Typography;

export const SCHEMA_OBJECT_NODE_TYPE = 'schemaObjectNode';

export type SchemaObjectNodeData = {
    name: string;
    physicalType?: string | null;
    properties: SchemaPropertyResponse[];
    fkPropertyIds: Set<string>;
    highlightedPropertyIds: Set<string>;
};

type SchemaObjectNodeType = Node<SchemaObjectNodeData>;

export function SchemaObjectNode({ data, selected }: NodeProps<SchemaObjectNodeType>) {
    const { name, physicalType, properties, fkPropertyIds, highlightedPropertyIds } = data;

    return (
        <Card
            size="small"
            title={name}
            extra={physicalType && <Tag>{physicalType}</Tag>}
            style={{ width: 280, borderColor: selected ? 'var(--ant-color-primary)' : undefined }}
        >
            <Table<SchemaPropertyResponse>
                size="small"
                showHeader={false}
                pagination={false}
                dataSource={properties}
                rowKey="id"
                onRow={(property) => ({
                    style: {
                        position: 'relative',
                        backgroundColor: highlightedPropertyIds.has(property.id)
                            ? 'var(--ant-color-primary-bg)'
                            : undefined,
                    },
                })}
                columns={[
                    {
                        key: 'name',
                        render: (_: unknown, property: SchemaPropertyResponse) => (
                            <>
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
                            </>
                        ),
                    },
                    {
                        key: 'type',
                        align: 'right',
                        render: (_: unknown, property: SchemaPropertyResponse) => (
                            <>
                                <Text type="secondary">{property.logical_type}</Text>
                                <DefaultHandle id={`${property.id}-source`} type="source" position={Position.Right} />
                            </>
                        ),
                    },
                ]}
            />
        </Card>
    );
}
