import { Card, Space, Table, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import type { SchemaPropertyResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetOutputPortSchemaQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

type Props = {
    datasetId: string;
    dataProductId: string;
};

function getPropertyColumns(t: ReturnType<typeof useTranslation>['t']) {
    return [
        {
            title: t('Name'),
            key: 'name',
            render: (_: unknown, record: SchemaPropertyResponse) => (
                <Space direction="vertical" size={0}>
                    <Typography.Text strong>{record.name}</Typography.Text>
                    {record.business_name && (
                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                            {record.business_name}
                        </Typography.Text>
                    )}
                </Space>
            ),
        },
        {
            title: t('Type'),
            key: 'type',
            render: (_: unknown, record: SchemaPropertyResponse) =>
                record.logical_type ? <Typography.Text type="secondary">{record.logical_type}</Typography.Text> : null,
        },
        {
            title: t('Required'),
            key: 'required',
            render: (_: unknown, record: SchemaPropertyResponse) =>
                record.required ? (
                    <Typography.Text type="secondary">{t('Yes')}</Typography.Text>
                ) : (
                    <Typography.Text type="secondary">{t('No')}</Typography.Text>
                ),
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            key: 'description',
            render: (description: string | null) =>
                description ? (
                    <Typography.Text>{description}</Typography.Text>
                ) : (
                    <Typography.Text type="secondary">—</Typography.Text>
                ),
        },
        {
            title: t('Example'),
            key: 'example',
            render: (_: unknown, record: SchemaPropertyResponse) => {
                const example = record.examples?.[0];
                return example != null ? (
                    <Typography.Text type="secondary" code>
                        {String(example)}
                    </Typography.Text>
                ) : null;
            },
        },
        {
            title: t('Flags'),
            key: 'flags',
            render: (_: unknown, record: SchemaPropertyResponse) => (
                <Space size={8}>
                    {record.primary_key && (
                        <Typography.Text style={{ color: '#1677ff', fontWeight: 500 }}>{t('PK')}</Typography.Text>
                    )}
                    {record.unique && (
                        <Typography.Text style={{ color: '#722ed1', fontWeight: 500 }}>{t('Unique')}</Typography.Text>
                    )}
                    {record.partitioned && (
                        <Typography.Text style={{ color: '#13c2c2', fontWeight: 500 }}>
                            {t('Partitioned')}
                        </Typography.Text>
                    )}
                </Space>
            ),
        },
    ];
}

export function DataModelTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data, isLoading } = useGetOutputPortSchemaQuery({ id: datasetId, dataProductId });

    if (isLoading) {
        return <LoadingSpinner />;
    }

    const schemaObjects = data?.schema_objects ?? [];

    if (schemaObjects.length === 0) {
        return <EmptyList description={t('No data model defined for this output port')} />;
    }

    const columns = getPropertyColumns(t);

    return (
        <>
            {schemaObjects.map((obj, index) => (
                <Card
                    key={obj.id}
                    size="small"
                    style={{ marginTop: index > 0 ? 16 : 0 }}
                    title={
                        <Space size="small">
                            <h3>{obj.name}</h3>
                            {obj.physical_type && <Tag>{obj.physical_type}</Tag>}
                        </Space>
                    }
                >
                    {obj.description ? (
                        <div style={{ marginBottom: 12 }}>
                            {obj.description && <Typography.Text type="secondary">{obj.description}</Typography.Text>}
                        </div>
                    ) : null}
                    <Table<SchemaPropertyResponse>
                        dataSource={obj.properties ?? []}
                        columns={columns}
                        rowKey="id"
                        size="small"
                        pagination={false}
                        locale={{ emptyText: t('No properties defined') }}
                    />
                </Card>
            ))}
        </>
    );
}
