import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { useCreateDataProductSettingMutation } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataProductSettingContract } from '@/types/data-product-setting';
import { generateExternalIdFromName } from '@/utils/external-id.helper';
import { Button, Form, Input, Select } from 'antd';
import { TFunction } from 'i18next';
const { Option } = Select;

interface CreateSettingModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
}

export const CreateSettingModal: React.FC<CreateSettingModalProps> = ({ isOpen, t, onClose }) => {
    const [form] = Form.useForm();
    const [createDataProductSetting, {isLoading: isCreating}] = useCreateDataProductSettingMutation();

    const handleFinish = async (values: any) => {
        try {
            const newSetting: DataProductSettingContract = {
                ...values,
                external_id: generateExternalIdFromName(values.name),
                order: parseInt(values.order, 10),
            };
            await createDataProductSetting(newSetting);
            dispatchMessage({ content: t('Data product setting created successfully'), type: 'success' });
            form.resetFields();
            onClose();
        }
        catch (_e) {
            const errorMessage = t('Failed to create data product setting');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t("Create New Data Product Setting")}
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
                    {t("Create")}
                </Button>,
                <Button
                    key="cancel"
                    onClick={() => {
                        form.resetFields();
                        onClose();
                    }}
                >
                    {t("Cancel")}
                </Button>,
            ]}
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={handleFinish}
                initialValues={{
                    type: 'checkbox',
                }}
            >
                <Form.Item name="name" label={t("Name")} rules={[{ required: true, message: t("Please input the name!") }]}>
                    <Input />
                </Form.Item>

                <Form.Item
                    name="tooltip"
                    label={t("Tooltip")}
                    rules={[{ required: true, message: t("Please input the tooltip!") }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="default"
                    label={t("Default Value")}
                    rules={[{ required: true, message: t("Please input the default value!") }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item name="type" label={t("Type")} rules={[{ required: true, message: t("Please select a type!") }]}>
                    <Select>
                        <Option value="checkbox">{t("Checkbox")}</Option>
                        <Option value="tags">{t("Tags")}</Option>
                        <Option value="input">{t("Input")}</Option>
                    </Select>
                </Form.Item>

                <Form.Item
                    name="divider"
                    label={t("Divider")}
                    rules={[{ required: true, message: t("Please input the divider!") }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="order"
                    label={t("Order")}
                    rules={[
                        { required: true, message: t("Please input the order!") },
                        { pattern: /^\d+$/, message: t("Order must be a number!") },
                    ]}
                >
                    <Input />
                </Form.Item>
            </Form>
        </FormModal>
    );
};
