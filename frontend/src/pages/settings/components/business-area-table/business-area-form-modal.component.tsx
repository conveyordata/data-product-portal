import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { Button, Form, Input } from 'antd';
import { TFunction } from 'i18next';
import {
    useCreateBusinessAreaMutation,
    useUpdateBusinessAreaMutation,
} from '@/store/features/business-areas/business-areas-api-slice';
import { BusinessAreaContract } from '@/types/business-area';

interface CreateBusinessAreaModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: BusinessAreaContract;
}

interface BusinessAreaFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

export const CreateBusinessAreaModal: React.FC<CreateBusinessAreaModalProps> = ({
    isOpen,
    t,
    onClose,
    mode,
    initial,
}) => {
    const [form] = Form.useForm();
    const [createBusinessArea, { isLoading: isCreating }] = useCreateBusinessAreaMutation();
    const [editBusinessArea, { isLoading: isEditing }] = useUpdateBusinessAreaMutation();

    const createText: BusinessAreaFormText = {
        title: t('Create New Business Area'),
        successMessage: t('Business Area created successfully'),
        errorMessage: t('Failed to create Business Area'),
        submitButtonText: t('Create'),
    };

    const updateText: BusinessAreaFormText = {
        title: t('Update Business Area'),
        successMessage: t('Business Area updated successfully'),
        errorMessage: t('Failed to update Business Area'),
        submitButtonText: t('Update'),
    };

    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (values: any) => {
        try {
            if (mode === 'create') {
                await createBusinessArea(values);
            } else {
                await editBusinessArea({ businessArea: values, businessAreaId: initial!.id });
            }

            dispatchMessage({ content: variableText.successMessage, type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = variableText.errorMessage;
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={variableText.title}
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
                    {variableText.submitButtonText}
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
            <Form form={form} layout="vertical" onFinish={handleFinish} initialValues={initial}>
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="description"
                    label={t('Description')}
                    rules={[{ required: true, message: t('Please provide a description') }]}
                >
                    <Input />
                </Form.Item>
            </Form>
        </FormModal>
    );
};
