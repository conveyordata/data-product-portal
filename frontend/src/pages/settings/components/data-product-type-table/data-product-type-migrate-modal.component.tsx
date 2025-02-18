import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { Button, Form, Input, Select } from 'antd';
import { TFunction } from 'i18next';

import { DataProductTypeContract } from '@/types/data-product-type';
import {
    useGetAllDataProductTypesQuery,
    useMigrateDataProductTypeMutation,
    useRemoveDataProductTypeMutation,
} from '@/store/features/data-product-types/data-product-types-api-slice';
const { Option } = Select;

interface CreateDataProductTypeMigrateModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    migrateFrom?: DataProductTypeContract;
}

export const CreateDataProductTypeMigrateModal: React.FC<CreateDataProductTypeMigrateModalProps> = ({
    isOpen,
    t,
    onClose,
    migrateFrom,
}) => {
    const [form] = Form.useForm();
    const { data: dataProductTypes = [], isFetching } = useGetAllDataProductTypesQuery();
    const [migrateDataProductType, { isLoading: isCreating }] = useMigrateDataProductTypeMutation();
    const [onRemoveDataProductType, { isLoading: isRemoving }] = useRemoveDataProductTypeMutation();

    const handleFinish = async (values: any) => {
        try {
            await migrateDataProductType({ fromId: migrateFrom!.id, toId: values.toId });
            await onRemoveDataProductType(migrateFrom!.id);
            dispatchMessage({ content: t('Data Product Type migrated and deleted successfully'), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t('Could not migrate or delete Data Product Type');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t('Migrate Data Product Type')}
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
                    {t('Submit')}
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
            <Form form={form} layout="vertical" onFinish={handleFinish} initialValues={migrateFrom}>
                <Form.Item name="name" label={t('Migrate from')}>
                    <Input defaultValue={migrateFrom?.name} disabled />
                </Form.Item>

                <Form.Item
                    name="toId"
                    label={t('Migrate to')}
                    rules={[{ required: true, message: t('Please provide a value') }]}
                >
                    <Select>
                        {dataProductTypes
                            .filter((dataProductType) => dataProductType.id !== migrateFrom!.id)
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
};
