import { Button, Form, Input, Select } from 'antd';

import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import {
    useGetAllDataProductTypesQuery,
    useMigrateDataProductTypeMutation,
    useRemoveDataProductTypeMutation,
} from '@/store/features/data-product-types/data-product-types-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type { DataProductTypeContract } from '@/types/data-product-type';
import { useTranslation } from 'react-i18next';

const { Option } = Select;

interface DataProductTypeMigrateFormValues {
    toId: string;
}

type Props = {
    onClose: () => void;
    isOpen: boolean;
    migrateFrom: DataProductTypeContract;
};
export function CreateDataProductTypeMigrateModal({ isOpen, onClose, migrateFrom }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const { data: dataProductTypes = [] } = useGetAllDataProductTypesQuery();
    const [migrateDataProductType] = useMigrateDataProductTypeMutation();
    const [onRemoveDataProductType] = useRemoveDataProductTypeMutation();

    const handleFinish = async (values: DataProductTypeMigrateFormValues) => {
        try {
            await migrateDataProductType({ fromId: migrateFrom?.id, toId: values.toId });
            await onRemoveDataProductType(migrateFrom?.id);
            dispatchMessage({ content: t('Type migrated and deleted successfully'), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t('Could not migrate or delete Type');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t('Delete Type')}
            onClose={() => {
                form.resetFields();
                onClose();
            }}
            onCancel={() => {
                form.resetFields();
                onClose();
            }}
            footer={[
                <Button key="submit" type="primary" danger onClick={() => form.submit()}>
                    {t('Delete')}
                </Button>,
                <Button
                    key="cancel"
                    danger
                    onClick={() => {
                        form.resetFields();
                        onClose();
                    }}
                >
                    {t('Cancel')}
                </Button>,
            ]}
        >
            <Form form={form} layout="vertical" onFinish={handleFinish} initialValues={migrateFrom}>
                <Form.Item name="name" label={t('Name')}>
                    <Input disabled />
                </Form.Item>

                <Form.Item
                    name="toId"
                    label={t('Migrate existing data products')}
                    rules={[{ required: true, message: t('Please provide a value') }]}
                >
                    <Select>
                        {dataProductTypes
                            .filter((dataProductType) => dataProductType.id !== migrateFrom?.id)
                            .map((dataProductType) => (
                                <Option key={dataProductType.id} value={dataProductType.id}>
                                    {dataProductType.name}
                                </Option>
                            ))}
                    </Select>
                </Form.Item>
            </Form>
        </FormModal>
    );
}
