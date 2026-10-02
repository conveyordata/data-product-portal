import { Form, Input, Modal, Radio, Select, Space, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { AccessModeSelector } from '@/components/data-products/technical-asset-form/access-mode-selector.component.tsx';
import {
    AssignmentFilter,
    AbstractDataProductStatus as DataProductStatus,
    useGetDataProductsQuery,
} from '@/store/api/services/generated/dataProductsApi.ts';
import {
    OutputPortAccessFunction,
    useGetOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    AbstractDataProductType,
    useGrantOutputPortAccessMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import {
    AbstractDataProductStatus as ExplorationStatus,
    useGetExplorationsQuery,
} from '@/store/api/services/generated/explorationsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

type FormValues = {
    consumerType: AbstractDataProductType;
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
    const isDataProduct = Form.useWatch('consumerType', form) !== AbstractDataProductType.Explorations;
    const { data: { data_products: dataProducts = [] } = {}, isFetching: isFetchingDataProducts } =
        useGetDataProductsQuery(AssignmentFilter.All, { skip: !isDataProduct });
    const { data: { explorations = [] } = {}, isFetching: isFetchingExplorations } = useGetExplorationsQuery(
        undefined,
        { skip: isDataProduct },
    );
    const { data: outputPort } = useGetOutputPortQuery({ dataProductId, id: outputPortId });
    const isInviteOnly = outputPort?.access_type.access_function === OutputPortAccessFunction.Private;
    const [grantOutputPortAccess, { isLoading }] = useGrantOutputPortAccessMutation();

    const consumerOptions = useMemo(() => {
        const consumers = isDataProduct
            ? dataProducts.filter((consumer) => consumer.status !== DataProductStatus.Deleting)
            : explorations.filter((consumer) => consumer.status !== ExplorationStatus.Deleting);
        return consumers
            .filter((consumer) => consumer.id !== dataProductId && !existingConsumerIds.includes(consumer.id))
            .map((consumer) => ({
                value: consumer.id,
                label: consumer.name,
                description: consumer.description,
            }));
    }, [isDataProduct, dataProducts, explorations, dataProductId, existingConsumerIds]);

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
            okText={t('Grant Access')}
            okButtonProps={{ disabled: isLoading || !outputPort }}
            cancelButtonProps={{ disabled: isLoading }}
        >
            <Form<FormValues>
                form={form}
                layout="vertical"
                initialValues={{ consumerType: AbstractDataProductType.DataProducts }}
                onFinish={onFinish}
                onFinishFailed={() =>
                    dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' })
                }
                disabled={isLoading}
            >
                <Form.Item<FormValues> name="consumerType" label={t('Consumer type')}>
                    <Radio.Group
                        optionType="button"
                        buttonStyle="solid"
                        options={[
                            { label: t('Data Product'), value: AbstractDataProductType.DataProducts },
                            {
                                label: t('Exploration'),
                                value: AbstractDataProductType.Explorations,
                                disabled: isInviteOnly,
                                title: isInviteOnly
                                    ? t('Explorations cannot consume Invite only Output Ports')
                                    : undefined,
                            },
                        ]}
                        onChange={() => form.setFieldValue('consumerId', undefined)}
                    />
                </Form.Item>
                <Form.Item<FormValues>
                    name="consumerId"
                    label={isDataProduct ? t('Data Product') : t('Exploration')}
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
