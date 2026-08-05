import { Button, Form, Input, Modal } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCreateTagMutation, useUpdateTagMutation } from '@/store/api/services/generated/configurationTagsApi.ts';
import type { TagContract } from '@/types/tag/tag';
import { dispatchMessage } from '@/utils/feedback.ts';

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
        title: t('Create new Tag'),
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
                await createTag(values).unwrap();
            } else {
                await editTag({ id: initial?.id ?? '', tagUpdate: { ...values } }).unwrap();
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
        <Modal
            open={isOpen}
            title={variableText.title}
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
            centered
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
        </Modal>
    );
}
