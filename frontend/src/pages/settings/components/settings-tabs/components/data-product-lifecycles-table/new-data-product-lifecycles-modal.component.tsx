import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import {
    useCreateDataProductLifecycleMutation,
    useUpdateDataProductLifecycleMutation,
} from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { Button, Checkbox, ColorPicker, Form, Input, InputNumber } from 'antd';
import { TFunction } from 'i18next';
import styles from './data-product-lifecycles-table.module.scss';

interface CreateLifecycleModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: DataProductLifeCycleContract;
}

interface LifeCycleFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

export const CreateLifecycleModal: React.FC<CreateLifecycleModalProps> = ({ isOpen, t, onClose, mode, initial }) => {
    const [form] = Form.useForm();
    const [createDataProductLifecycle, { isLoading: isCreating }] = useCreateDataProductLifecycleMutation();
    const [editDataProductLifecycle, { isLoading: isEditing }] = useUpdateDataProductLifecycleMutation();

    const createText: LifeCycleFormText = {
        title: t('Create New Lifecycle'),
        successMessage: t('lifecycle created successfully'),
        errorMessage: t('Failed to create lifecycle'),
        submitButtonText: t('Create'),
    };

    const updateText: LifeCycleFormText = {
        title: t('Update Lifecycle'),
        successMessage: t('lifecycle updated successfully'),
        errorMessage: t('Failed to update lifecycle'),
        submitButtonText: t('Update'),
    };

    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (lifeCycle: DataProductLifeCycleContract) => {
        try {
            if (mode === 'create') {
                await createDataProductLifecycle(lifeCycle);
            } else {
                await editDataProductLifecycle(lifeCycle);
            }
            dispatchMessage({ content: variableText.successMessage, type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            dispatchMessage({ content: variableText.errorMessage, type: 'error' });
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
            <Form
                form={form}
                layout="vertical"
                onFinish={handleFinish}
                initialValues={initial || { is_default: false }}
            >
                <Form.Item name={'id'} hidden />
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="value"
                    label={t('Value')}
                    rules={[
                        { required: true, message: t('Please provide a value') },
                        { type: 'number', message: t('Value must be a number') },
                    ]}
                >
                    <InputNumber min={0} precision={0} className={styles.numberInput} />
                </Form.Item>

                <Form.Item
                    name="color"
                    label={t('Color')}
                    rules={[{ required: true, message: t('Please pick a color') }]}
                    normalize={(color) => color.toHexString()}
                >
                    <ColorPicker format="hex" />
                </Form.Item>
                <Form.Item
                    name="is_default"
                    label={t('Is Default')}
                    valuePropName="checked"
                    tooltip={t('You can only have one default lifecycle')}
                    rules={[{ required: true, message: t('You can only have one default lifecycle') }]}
                >
                    <Checkbox disabled />
                </Form.Item>
            </Form>
        </FormModal>
    );
};
