import { Form, Input, Modal, Radio, Select, Space, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AccessModeSelector } from '@/components/data-products/technical-asset-form/access-mode-selector.component.tsx';
import {
    AssignmentFilter,
    AbstractDataProductStatus as DataProductStatus,
    useGetDataProductsQuery,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGrantOutputPortAccessMutation } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import {
    AbstractDataProductStatus as ExplorationStatus,
    useGetExplorationsQuery,
} from '@/store/api/services/generated/explorationsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

type ConsumerType = 'data_product' | 'exploration';

type FormValues = {
    consumerType: ConsumerType;
    consumerId: string;
    justification: string;
    accessModeIds?: string[];
};

type Props = {
    dataProductId: string;
    outputPortId: string;
    existingConsumerIds: string[];
    onClose: () => void;
};

export function GrantOutputPortAccessModal({ dataProductId, outputPortId, existingConsumerIds, onClose }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm<FormValues>();
    const [consumerType, setConsumerType] = useState<ConsumerType>('data_product');
    const { data: { data_products: dataProducts = [] } = {}, isFetching: isFetchingDataProducts } =
        useGetDataProductsQuery(AssignmentFilter.All, { skip: consumerType !== 'data_product' });
    const { data: { explorations = [] } = {}, isFetching: isFetchingExplorations } = useGetExplorationsQuery(
        undefined,
        {
            skip: consumerType !== 'exploration',
        },
    );
    const { data: outputPort } = useGetOutputPortQuery({ dataProductId, id: outputPortId });
    const [grantOutputPortAccess, { isLoading }] = useGrantOutputPortAccessMutation();
    const existingConsumerIdSet = useMemo(() => new Set(existingConsumerIds), [existingConsumerIds]);

    const consumerOptions = useMemo(() => {
        const consumers =
            consumerType === 'data_product'
                ? dataProducts.filter((consumer) => consumer.status !== DataProductStatus.Deleting)
                : explorations.filter((consumer) => consumer.status !== ExplorationStatus.Deleting);
        return consumers
            .filter((consumer) => consumer.id !== dataProductId && !existingConsumerIdSet.has(consumer.id))
            .map((consumer) => ({
                value: consumer.id,
                label: consumer.name,
                description: consumer.description,
            }));
    }, [consumerType, dataProducts, explorations, dataProductId, existingConsumerIdSet]);

    const onFinish = async (values: FormValues) => {
        try {
            await grantOutputPortAccess({
                dataProductId,
                outputPortId,
                grantOutputPortAccessRequest: {
                    consuming_abstract_data_product_id: values.consumerId,
                    justification: values.justification,
                    access_mode_id: values.accessModeIds?.[0],
                },
            }).unwrap();
            dispatchMessage({ content: t('Consumer access has been granted'), type: 'success' });
            onClose();
        } catch (_error) {
            dispatchMessage({ content: t('Failed to grant consumer access'), type: 'error' });
        }
    };

    return (
        <Modal
            title={t('Add consumer')}
            open
            centered
            onCancel={onClose}
            onOk={() => form.submit()}
            confirmLoading={isLoading}
            okText={t('Grant access')}
            okButtonProps={{ disabled: isLoading }}
            cancelButtonProps={{ disabled: isLoading }}
        >
            <Form<FormValues>
                form={form}
                layout="vertical"
                initialValues={{ consumerType }}
                onFinish={onFinish}
                disabled={isLoading}
            >
                <Form.Item<FormValues> name="consumerType" label={t('Consumer type')}>
                    <Radio.Group
                        optionType="button"
                        buttonStyle="solid"
                        options={[
                            { label: t('Data Product'), value: 'data_product' },
                            { label: t('Exploration'), value: 'exploration' },
                        ]}
                        onChange={(event) => {
                            setConsumerType(event.target.value);
                            form.setFieldValue('consumerId', undefined);
                        }}
                    />
                </Form.Item>
                <Form.Item<FormValues>
                    name="consumerId"
                    label={consumerType === 'data_product' ? t('Data Product') : t('Exploration')}
                    rules={[{ required: true, message: t('Please select a consumer') }]}
                >
                    <Select
                        placeholder={t('Search consumers')}
                        loading={isFetchingDataProducts || isFetchingExplorations}
                        showSearch={{ optionFilterProp: 'label' }}
                        options={consumerOptions}
                        optionRender={(option) => (
                            <Space vertical>
                                <Typography.Text>{option.data.label}</Typography.Text>
                                <Typography.Text type="secondary">{option.data.description}</Typography.Text>
                            </Space>
                        )}
                    />
                </Form.Item>
                <Form.Item<FormValues>
                    name="justification"
                    label={t('Business justification')}
                    rules={[{ required: true, message: t('Please provide a business justification') }]}
                >
                    <Input.TextArea autoSize={{ minRows: 3, maxRows: 8 }} />
                </Form.Item>
                {outputPort && outputPort.access_modes.length > 0 && (
                    <Form.Item<FormValues>
                        name="accessModeIds"
                        label={t('Access mode')}
                        rules={[{ required: true, message: t('Please select an access mode') }]}
                    >
                        <AccessModeSelector selectionMode="single" accessModes={outputPort.access_modes} />
                    </Form.Item>
                )}
            </Form>
        </Modal>
    );
}
