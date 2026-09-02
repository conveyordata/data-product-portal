import { DatabaseOutlined, SafetyOutlined, UploadOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import type { UploadProps } from 'antd';
import { Alert, Button, Empty, Flex, Space, Typography, Upload } from 'antd';
import { useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetOutputPortSchemaQuery,
    useIngestOutputPortContractYamlMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { dispatchMessage } from '@/utils/feedback.ts';
import styles from './data-model-tab.module.scss';
import { SchemaDiagram } from './schema-diagram/schema-diagram.tsx';

const { Text, Title, Paragraph } = Typography;

type Props = {
    datasetId: string;
    dataProductId: string;
};

type UploadRequestOptions = Parameters<NonNullable<UploadProps['customRequest']>>[0];

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
                    {canUpload && (
                        <Alert
                            type="info"
                            icon={<SafetyOutlined />}
                            showIcon
                            title={t('As an owner you can upload a schema')}
                            description={
                                <Space orientation="vertical" size="small">
                                    <a
                                        href="https://docs.dataproductportal.com/docs/developer-guide/schema-information"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        {t('Learn how to upload a schema in the docs')}
                                    </a>
                                    <Space size="small">
                                        <Text>{t('Or upload a schema now')}</Text>
                                        {uploadButton}
                                    </Space>
                                </Space>
                            }
                        />
                    )}
                </Empty>
            </Flex>
        );
    }

    return (
        <Flex vertical gap={12}>
            {uploadButton && <Flex justify="end">{uploadButton}</Flex>}
            <SchemaDiagram
                schemaObjects={schemaObjects}
                declaredRelationships={data?.relationships}
                onSelectObject={(key) => posthog.capture(PosthogEvents.OUTPUT_PORT_DATA_MODEL_TABLE, { tab: key })}
            />
        </Flex>
    );
}
