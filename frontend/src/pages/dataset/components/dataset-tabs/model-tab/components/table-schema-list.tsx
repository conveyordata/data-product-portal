import { Collapse, Flex, Tag, Typography } from 'antd';
import type { TableSchemaResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { ColumnTable } from './column-table';

type Props = {
    schemas: TableSchemaResponse[];
};

export function TableSchemaList({ schemas }: Props) {
    const items = schemas.map((schema) => ({
        key: schema.id,
        label: (
            <Flex gap="small" align="center" wrap>
                <Typography.Text strong>{schema.name}</Typography.Text>
                {schema.description && <Typography.Text type="secondary">{schema.description}</Typography.Text>}
                {schema.tags.map((tag) => (
                    <Tag key={tag.id}>{tag.value}</Tag>
                ))}
            </Flex>
        ),
        children: <ColumnTable columns={schema.columns} />,
    }));

    return <Collapse items={items} />;
}
