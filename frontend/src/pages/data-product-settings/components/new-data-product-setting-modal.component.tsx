import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { useCreateDataProductSettingMutation } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataProductSettingContract } from '@/types/data-product-setting';
import { generateExternalIdFromName } from '@/utils/external-id.helper';
import { Button, Checkbox, Form, Input, Select } from 'antd';
import { TFunction } from 'i18next';
import { useEffect } from 'react';
import styles from '@/components/data-products/data-output-form/data-output-form.module.scss';
const { Option } = Select;

interface CreateSettingModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
}

export const CreateSettingModal: React.FC<CreateSettingModalProps> = ({ isOpen, t, onClose }) => {
    const [form] = Form.useForm();
    const [createDataProductSetting, { isLoading: isCreating }] = useCreateDataProductSettingMutation();
    const typeValue = Form.useWatch('type', form);

    const handleFinish = async (values: any) => {
        try {
            const newSetting: DataProductSettingContract = {
                ...values,
                default: values.default.toString(),
                external_id: generateExternalIdFromName(values.name),
                order: parseInt(values.order, 10),
            };
            await createDataProductSetting(newSetting);
            dispatchMessage({ content: t('Data product setting created successfully'), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t('Failed to create data product setting');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    useEffect(() => {
        form.resetFields(['default']);
    }, [typeValue]);

    return (
        <FormModal
            isOpen={isOpen}
            title={t('Create New Data Product Setting')}
            onClose={() => {
                form.resetFields();
                onClose();
            }}
            onCancel={() => {
                form.resetFields();
                onClose();
            }}
            footer={[
                <Button key="submit" type="primary" onClick={() => form.submit()}>
                    {t('Create')}
                </Button>,
                <Button
                    key="cancel"
                    onClick={() => {
                        form.resetFields();
                        onClose();
                    }}
                >
                    {t('Cancel')}
                </Button>,
            ]}
        >
            <Form
                className={styles.form}
                form={form}
                layout="vertical"
                onFinish={handleFinish}
                initialValues={{
                    type: 'checkbox',
                    default: (() => {
                        switch (typeValue) {
                            case 'checkbox':
                                return true;
                            case 'tags':
                                return [];
                            case 'input':
                                return '';
                            default:
                                return '';
                        }
                    })(),
                }}
            >
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="tooltip"
                    label={t('Tooltip')}
                    rules={[{ required: true, message: t('Please provide a tooltip') }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="type"
                    label={t('Type')}
                    rules={[{ required: true, message: t('Please select a type') }]}
                >
                    <Select>
                        <Option value="checkbox">{t('Checkbox')}</Option>
                        <Option value="tags">{t('List')}</Option>
                        <Option value="input">{t('Input')}</Option>
                    </Select>
                </Form.Item>

                <Form.Item
                    name="default"
                    label={t('Default Value')}
                    rules={[{ required: true, message: t('Please provide a default value') }]}
                    valuePropName={typeValue === 'checkbox' ? 'checked' : 'value'}
                >
                    {(() => {
                        switch (typeValue) {
                            case 'checkbox':
                                return <Checkbox defaultChecked={true}></Checkbox>;
                            case 'tags':
                                return <Select allowClear={false} defaultActiveFirstOption mode="tags" />;
                            case 'input':
                                return <Input />;
                            default:
                                return <Input />;
                        }
                    })()}
                </Form.Item>
                <Form.Item
                    name="divider"
                    label={t('Divider')}
                    rules={[{ required: true, message: t('Please provide a divider') }]}
                    tooltip={t('The divider breaks up the settings into sections')}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="order"
                    label={t('Order')}
                    rules={[
                        { required: true, message: t('Please provide an order') },
                        { pattern: /^\d+$/, message: t('Order must be a number') },
                    ]}
                    tooltip={t('The order in which the setting will appear, within their own section')}
                >
                    <Input />
                </Form.Item>
            </Form>
        </FormModal>
    );
};
