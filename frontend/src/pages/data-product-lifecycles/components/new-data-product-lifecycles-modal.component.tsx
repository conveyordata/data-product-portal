import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { useCreateDataProductLifecycleMutation } from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { generateExternalIdFromName } from '@/utils/external-id.helper';
import { Button, Checkbox, ColorPicker, Form, Input, Select } from 'antd';
import { TFunction } from 'i18next';
const { Option } = Select;

interface CreateLifecycleModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
}

export const CreateLifecycleModal: React.FC<CreateLifecycleModalProps> = ({ isOpen, t, onClose }) => {
    const [form] = Form.useForm();
    const [createDataProductLifecycle, {isLoading: isCreating}] = useCreateDataProductLifecycleMutation();

    const handleFinish = async (values: any) => {
        try {
            const newLifecycle: DataProductLifeCycleContract = {
                ...values, color: values.color.toHexString()
            };
            await createDataProductLifecycle(newLifecycle);
            dispatchMessage({ content: t('Data product lifecycle created successfully'), type: 'success' });
            form.resetFields();
            onClose();
        }
        catch (_e) {
            const errorMessage = t('Failed to create data product lifecycle');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t("Create New Data Product Lifecycle")}
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
                <Form.Item name="name" label={t("Name")} rules={[{ required: true, message: t("Please provide a name") }]}>
                    <Input />
                </Form.Item>

                <Form.Item
                    name="value"
                    label={t("Value")}
                    rules={[{ required: true, message: t("Please provide a value") }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="color"
                    label={t("Color")}
                    rules={[{ required: true, message: t("Please pick a color") }]}
                >
                    <ColorPicker />
                </Form.Item>
                <Form.Item
                    name="is_default"
                    label={t("Is Default")}
                    tooltip={t("You can only have one default lifecycle")}
                    rules={[{ required: true, message: t("You can only have one default lifecycle") }]}
                    initialValue={false}
                >
                    <Checkbox checked={false} disabled={true}/>
                </Form.Item>
            </Form>
        </FormModal>
    );
};
