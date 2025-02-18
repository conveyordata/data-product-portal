import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { Button, Form, Input, Select } from 'antd';
import { TFunction } from 'i18next';
import {
    useGetAllBusinessAreasQuery,
    useMigrateBusinessAreaMutation,
    useRemoveBusinessAreaMutation,
} from '@/store/features/business-areas/business-areas-api-slice';
import { BusinessAreaContract } from '@/types/business-area';
const { Option } = Select;

interface CreateBusinessAreaMigrateModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    migrateFrom?: BusinessAreaContract;
}

export const CreateBusinessAreaMigrateModal: React.FC<CreateBusinessAreaMigrateModalProps> = ({
    isOpen,
    t,
    onClose,
    migrateFrom,
}) => {
    const [form] = Form.useForm();
    const { data: businessAreas = [], isFetching } = useGetAllBusinessAreasQuery();
    const [migrateBusinessArea, { isLoading: isCreating }] = useMigrateBusinessAreaMutation();
    const [onRemoveBusinessArea, { isLoading: isRemoving }] = useRemoveBusinessAreaMutation();

    const handleFinish = async (values: any) => {
        try {
            await migrateBusinessArea({ fromId: migrateFrom!.id, toId: values.toId });
            await onRemoveBusinessArea(migrateFrom!.id);
            dispatchMessage({ content: t('Business Area migrated and deleted successfully'), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t('Could not migrate or delete Business Area');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t('Migrate Business Area')}
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
                    rules={[{ required: true, message: t('Please provide a description') }]}
                >
                    <Select>
                        {businessAreas
                            .filter((businessArea) => businessArea.id !== migrateFrom!.id)
                            .map((businessArea) => (
                                <Option key={businessArea.id} value={businessArea.id}>
                                    {businessArea.name}
                                </Option>
                            ))}
                    </Select>
                </Form.Item>
            </Form>
        </FormModal>
    );
};
