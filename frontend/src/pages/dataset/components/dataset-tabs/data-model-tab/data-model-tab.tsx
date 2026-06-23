import { usePostHog } from '@posthog/react';
import { BookOutlined, DatabaseOutlined, SafetyOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Empty, Flex, Space, Table, Tag, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import type { SchemaPropertyResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetOutputPortSchemaQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import styles from './data-model-tab.module.scss';

const { Text, Title, Paragraph } = Typography;

type Props = {
    datasetId: string;
    dataProductId: string;
};

function getPropertyColumns(t: TFunction) {
    return [
        {
            title: t('Name'),
            key: 'name',
            render: (_: unknown, record: SchemaPropertyResponse) => (
                <Space orientation="vertical" size={0}>
                    <Text strong>{record.name}</Text>
                    {record.business_name && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                            {record.business_name}
                        </Text>
                    )}
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
                    {record.primary_key && <Text className={styles['primary-key-flag']}>{t('PK')}</Text>}
                    {record.unique && <Text className={styles['unique-flag']}>{t('Unique')}</Text>}
                    {record.partitioned && <Text className={styles['partitioned-flag']}>{t('Partitioned')}</Text>}
                </Space>
            ),
        },
    ];
}

export function DataModelTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const { data, isLoading } = useGetOutputPortSchemaQuery({ id: datasetId, dataProductId });
    const schemaObjects = data?.schema_objects ?? [];

    const [activeTab, setActiveTab] = useState<string | undefined>(undefined);

    useEffect(() => {
        if (!isLoading && data !== undefined) {
            posthog.capture(PosthogEvents.OUTPUT_PORT_DATA_MODEL_LOADED, {
                data_model_defined: data?.schema_objects?.length !== 0,
            });
        }
    }, [isLoading, data, posthog]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    if (schemaObjects.length === 0) {
        return (
            <Flex justify="center" className={styles.emptyContainer}>
                <Empty
                    image={<DatabaseOutlined className={styles.emptyIcon} />}
                    style={{ maxWidth: 480 }}
                    description={
                        <>
                            <Title level={4}>{t('Data Model not published yet')}</Title>
                            <Paragraph type="secondary">
                                {t(
                                    "The owner of this Output Port hasn't defined a data model. Reach out to them directly to request it.",
                                )}
                            </Paragraph>
                        </>
                    }
                >
                    <Alert
                        type="info"
                        icon={<SafetyOutlined />}
                        showIcon
                        title={t('Are you the owner?')}
                        action={
                            <Button
                                icon={<BookOutlined />}
                                href={'https://docs.dataproductportal.com/docs/developer-guide/schema-information'}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {t('How to add a schema')}
                            </Button>
                        }
                    />
                </Empty>
            </Flex>
        );
    }

    const tabList = schemaObjects.map((schema) => ({
        key: schema.id,
        label: (
            <Space size="small">
                <Text strong style={{ color: 'inherit' }}>
                    {schema.name}
                </Text>
                {schema.physical_type && <Tag style={{ color: 'inherit' }}>{schema.physical_type}</Tag>}
            </Space>
        ),
    }));

    const renderSchema = (activeKey: string | undefined) => {
        const schema = schemaObjects.find((schema) => schema.id === activeKey) ?? schemaObjects[0];
        return (
            <>
                {((schema?.physical_name && schema?.physical_name !== schema.name) || schema?.description) && (
                    <Space style={{ margin: '0 8px 12px' }}>
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
            </>
        );
    };

    return (
        <Card
            size="small"
            tabList={tabList}
            onTabChange={(key: string) => {
                posthog.capture(PosthogEvents.OUTPUT_PORT_DATA_MODEL_TABLE, { tab: key });
                setActiveTab(key);
            }}
        >
            {renderSchema(activeTab)}
        </Card>
    );
}
