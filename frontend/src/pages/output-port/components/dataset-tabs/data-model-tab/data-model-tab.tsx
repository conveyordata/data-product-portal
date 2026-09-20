import { FileTextOutlined, UploadOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import type { UploadProps } from 'antd';
import { Button, Flex, Space, Table, Tabs, Tag, Typography, Upload } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import type { SchemaPropertyResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    useGetOutputPortSchemaQuery,
    useIngestOutputPortContractYamlMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { dispatchMessage } from '@/utils/feedback.ts';
import styles from './data-model-tab.module.scss';

const { Text } = Typography;

type Props = {
    datasetId: string;
    dataProductId: string;
};

type UploadRequestOptions = Parameters<NonNullable<UploadProps['customRequest']>>[0];

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
    const { data, isLoading, refetch } = useGetOutputPortSchemaQuery({ id: datasetId, dataProductId });
    const [uploadContract, { isLoading: isUploading }] = useIngestOutputPortContractYamlMutation();
    const { data: access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_CONTRACT,
        },
        { skip: !datasetId },
    );
    const canUpload = access?.allowed || false;
    const schemaObjects = data?.schema_objects ?? [];

    useEffect(() => {
        if (!isLoading && data !== undefined) {
            posthog.capture(PosthogEvents.OUTPUT_PORT_DATA_MODEL_LOADED, {
                data_model_defined: data?.schema_objects?.length !== 0,
            });
        }
    }, [isLoading, data, posthog]);

    const uploadDataModelCustomRequest = useCallback(
        async (options: UploadRequestOptions) => {
            const file = options.file;

            if (typeof file === 'string') {
                throw new Error('Schema upload requires a binary file.');
            }

            try {
                const formData = new FormData();
                formData.append('file', file);

                await uploadContract({
                    id: datasetId,
                    dataProductId,
                    body: formData as never,
                }).unwrap();
                await refetch();
                options.onSuccess?.({}, options.file);
                dispatchMessage({ content: t('Schema uploaded successfully'), type: 'success' });
            } catch (_error) {
                options.onError?.(new Error('upload failed'));
                dispatchMessage({ content: t('Could not upload schema file'), type: 'error' });
            }
        },
        [dataProductId, datasetId, refetch, t, uploadContract],
    );

    const uploadButton = canUpload ? (
        <Upload
            accept=".yaml,.yml"
            maxCount={1}
            showUploadList={false}
            disabled={isUploading}
            customRequest={uploadDataModelCustomRequest}
        >
            <Button type="primary" icon={<UploadOutlined />} loading={isUploading}>
                {t('Upload schema')}
            </Button>
        </Upload>
    ) : null;

    if (isLoading) {
        return <LoadingSpinner />;
    }

    if (schemaObjects.length === 0) {
        return (
            <EmptyState
                icon={<FileTextOutlined />}
                title={t('No Data Model published yet')}
                description={
                    canUpload
                        ? t('Upload a schema to document the tables and columns behind this Output Port.')
                        : t(
                              "The owner of this Output Port hasn't published a data model. Reach out to them to request one.",
                          )
                }
                action={
                    canUpload && (
                        <Flex align="center" gap="small" wrap justify="center">
                            {uploadButton}
                            <a
                                href="https://docs.dataproductportal.com/docs/developer-guide/schema-information"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {t('Learn how to upload a schema')}
                            </a>
                        </Flex>
                    )
                }
            />
        );
    }

    const tabs = schemaObjects.map((schema) => ({
        key: schema.id,
        label: (
            <Space size="small">
                <Text strong style={{ color: 'inherit' }}>
                    {schema.name}
                </Text>
                {schema.physical_type && <Tag style={{ color: 'inherit' }}>{schema.physical_type}</Tag>}
            </Space>
        ),
        children: (
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
                    locale={{
                        emptyText: (
                            <EmptyState
                                icon={<FileTextOutlined />}
                                title={t('No columns defined')}
                                description={t('This table is published without column level detail.')}
                            />
                        ),
                    }}
                />
            </>
        ),
    }));

    return (
        <Tabs
            defaultActiveKey={schemaObjects[0]?.id}
            items={tabs}
            tabBarExtraContent={uploadButton ? { right: uploadButton } : undefined}
            onChange={(key: string) => {
                posthog.capture(PosthogEvents.OUTPUT_PORT_DATA_MODEL_TABLE, { tab: key });
            }}
        />
    );
}
