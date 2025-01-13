import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { useCreateDataProductSettingMutation } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { DataProductSettingContract } from '@/types/data-product-setting';
import { generateExternalIdFromName } from '@/utils/external-id.helper';
import { Button, Form, Input, Select } from 'antd';
const { Option } = Select;

interface CreateSettingModalProps {
    onClose: () => void;
    isOpen: boolean;
}

export const CreateSettingModal: React.FC<CreateSettingModalProps> = ({ isOpen, onClose }) => {
    const [form] = Form.useForm();
    const [createDataProductSetting, {isLoading: isCreating}] = useCreateDataProductSettingMutation();

    const handleFinish = (values: any) => {
        const newSetting: DataProductSettingContract = {
            ...values,
            external_id: generateExternalIdFromName(values.name),
            order: parseInt(values.order, 10),
        };
        createDataProductSetting(newSetting);
        form.resetFields();
        onClose();
    };

    return (
        <FormModal
            isOpen={isOpen}
            title="Create New Data Product Setting"
            onClose={() => {
                form.resetFields();
                onClose();
            }}
            onCancel={() => {
                form.resetFields();
                onClose();
            }}
            footer={[
                <Button
                    key="cancel"
                    onClick={() => {
                        form.resetFields();
                        onClose();
                    }}
                >
                    Cancel
                </Button>,
                <Button key="submit" type="primary" onClick={() => form.submit()}>
                    Create
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
                <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input the name!' }]}>
                    <Input />
                </Form.Item>

                <Form.Item
                    name="tooltip"
                    label="Tooltip"
                    rules={[{ required: true, message: 'Please input the tooltip!' }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="default"
                    label="Default Value"
                    rules={[{ required: true, message: 'Please input the default value!' }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item name="type" label="Type" rules={[{ required: true, message: 'Please select a type!' }]}>
                    <Select>
                        <Option value="checkbox">Checkbox</Option>
                        <Option value="tags">Tags</Option>
                        <Option value="input">Input</Option>
                    </Select>
                </Form.Item>

                <Form.Item
                    name="divider"
                    label="Divider"
                    rules={[{ required: true, message: 'Please input the divider!' }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="order"
                    label="Order"
                    rules={[
                        { required: true, message: 'Please input the order!' },
                        { pattern: /^\d+$/, message: 'Order must be a number!' },
                    ]}
                >
                    <Input />
                </Form.Item>
            </Form>
        </FormModal>
    );
};
