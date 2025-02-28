import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { Button, Form, Input, Select } from 'antd';
import { TFunction } from 'i18next';
import { DataProductTypeContract } from '@/types/data-product-type';
import {
    useCreateDataProductTypeMutation,
    useUpdateDataProductTypeMutation,
} from '@/store/features/data-product-types/data-product-types-api-slice';
import { DataProductIcon, dataProductIcons } from '@/types/data-product-type/data-product-type.contract';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import Icon from '@ant-design/icons';
import styles from './data-product-type-table.module.scss';

const { Option } = Select;

interface CreateDataProductTypeModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: DataProductTypeContract;
}

interface DataProductTypeFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

export const CreateDataProductTypeModal: React.FC<CreateDataProductTypeModalProps> = ({
    isOpen,
    t,
    onClose,
    mode,
    initial,
}) => {
    const [form] = Form.useForm();
    const [createDataProductType] = useCreateDataProductTypeMutation();
    const [editDataProductType] = useUpdateDataProductTypeMutation();

    const createText: DataProductTypeFormText = {
        title: t('Create New Data Product Type'),
        successMessage: t('Data Product Type created successfully'),
        errorMessage: t('Failed to create Data Product Type'),
        submitButtonText: t('Create'),
    };

    const updateText: DataProductTypeFormText = {
        title: t('Update New Data Product Type'),
        successMessage: t('Data Product Type updated successfully'),
        errorMessage: t('Failed to update Data Product Type'),
        submitButtonText: t('Update'),
    };

    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (values: any) => {
        try {
            if (mode === 'create') {
                await createDataProductType(values);
            } else {
                await editDataProductType({ dataProductType: values, dataProductTypeId: initial!.id });
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

                <Form.Item
                    name="icon_key"
                    label={t('Icon')}
                    rules={[{ required: true, message: t('Please provide an icon') }]}
                >
                    <Select>
                        {dataProductIcons
                            .filter((icon) => icon !== DataProductIcon.Default)
                            .map((icon) => (
                                <Option key={icon} value={icon}>
                                    <Icon component={getDataProductTypeIcon(icon)} className={styles.iconSelect} />
                                </Option>
                            ))}
                    </Select>
                </Form.Item>
            </Form>
        </FormModal>
    );
};
