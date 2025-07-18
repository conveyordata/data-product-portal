import { Button, Form, Input } from 'antd';
import { useTranslation } from 'react-i18next';
import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { useCreateDomainMutation, useUpdateDomainMutation } from '@/store/features/domains/domains-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type { DomainContract, DomainCreateRequest } from '@/types/domain';

interface DomainFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

type Props = {
    onClose: () => void;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: DomainContract;
};
export function CreateDomainModal({ isOpen, onClose, mode, initial }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const [createDomain] = useCreateDomainMutation();
    const [editDomain] = useUpdateDomainMutation();

    const createText: DomainFormText = {
        title: t('Create New Domain'),
        successMessage: t('Domain created successfully'),
        errorMessage: t('Failed to create Domain'),
        submitButtonText: t('Create'),
    };

    const updateText: DomainFormText = {
        title: t('Update Domain'),
        successMessage: t('Domain updated successfully'),
        errorMessage: t('Failed to update Domain'),
        submitButtonText: t('Update'),
    };

    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (values: DomainCreateRequest) => {
        try {
            if (mode === 'create') {
                await createDomain(values);
            } else {
                await editDomain({ domain: values, domainId: initial?.id || '' });
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
}
