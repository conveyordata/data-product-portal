import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { useCreateTagMutation, useUpdateTagMutation } from '@/store/features/tags/tags-api-slice';
import { TagContract } from '@/types/tag';
import { Button, Form, Input } from 'antd';
import { TFunction } from 'i18next';

interface CreateTagsModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: TagContract;
}

interface TagsFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

const createText: TagsFormText = {
    title: 'Create New Tag',
    successMessage: 'Tag created successfully',
    errorMessage: 'Failed to create tag',
    submitButtonText: 'Create',
};

const updateText: TagsFormText = {
    title: 'Update Tag',
    successMessage: 'Tag updated successfully',
    errorMessage: 'Failed to update tag',
    submitButtonText: 'Update',
};

export const CreateTagsModal: React.FC<CreateTagsModalProps> = ({ isOpen, t, onClose, mode, initial }) => {
    const [form] = Form.useForm();
    const [createTag, { isLoading: isCreating }] = useCreateTagMutation();
    const [editTag, { isLoading: isEditing }] = useUpdateTagMutation();
    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (values: any) => {
        try {
            if (mode === 'create') {
                await createTag(values);
            } else {
                await editTag({ tag: values, tagId: initial!.id });
            }

            dispatchMessage({ content: t(variableText.successMessage), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t(variableText.errorMessage);
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t(variableText.title)}
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
                    {t(variableText.submitButtonText)}
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
                    name="value"
                    label={t('Value')}
                    rules={[{ required: true, message: t('Please provide a value') }]}
                >
                    <Input />
                </Form.Item>
            </Form>
        </FormModal>
    );
};
