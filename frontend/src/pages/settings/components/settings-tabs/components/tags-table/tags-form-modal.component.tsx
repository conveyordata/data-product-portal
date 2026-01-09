import { Button, Form, Input } from 'antd';
import { useTranslation } from 'react-i18next';
import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { useCreateTagMutation, useUpdateTagMutation } from '@/store/api/services/generated/configurationTagsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type { TagContract } from '@/types/tag';

interface TagsFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

type Props = {
    onClose: () => void;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: TagContract;
};
export function CreateTagsModal({ isOpen, onClose, mode, initial }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const [createTag] = useCreateTagMutation();
    const [editTag] = useUpdateTagMutation();

    const createText: TagsFormText = {
        title: t('Create New Tag'),
        successMessage: t('Tag created successfully'),
        errorMessage: t('Failed to create tag'),
        submitButtonText: t('Create'),
    };

    const updateText: TagsFormText = {
        title: t('Update Tag'),
        successMessage: t('Tag updated successfully'),
        errorMessage: t('Failed to update tag'),
        submitButtonText: t('Update'),
    };

    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (values: TagContract) => {
        try {
            if (mode === 'create') {
                await createTag(values);
            } else {
                await editTag({ id: initial?.id ?? '', tagUpdate: { ...values } });
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
                    name="value"
                    label={t('Value')}
                    rules={[{ required: true, message: t('Please provide a value') }]}
                >
                    <Input />
                </Form.Item>
            </Form>
        </FormModal>
    );
}
