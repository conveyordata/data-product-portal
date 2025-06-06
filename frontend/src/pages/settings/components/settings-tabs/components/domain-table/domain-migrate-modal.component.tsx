import { Button, Form, Input, Select } from 'antd';

import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import {
    useGetAllDomainsQuery,
    useMigrateDomainMutation,
    useRemoveDomainMutation,
} from '@/store/features/domains/domains-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type { DomainContract } from '@/types/domain';
import { useTranslation } from 'react-i18next';

const { Option } = Select;

interface DomainMigrateFormValues {
    toId: string;
}

type Props = {
    onClose: () => void;
    isOpen: boolean;
    migrateFrom: DomainContract;
};
export function CreateDomainMigrateModal({ isOpen, onClose, migrateFrom }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const { data: domains = [] } = useGetAllDomainsQuery();
    const [migrateDomain] = useMigrateDomainMutation();
    const [onRemoveDomain] = useRemoveDomainMutation();

    const handleFinish = async (values: DomainMigrateFormValues) => {
        try {
            await migrateDomain({ fromId: migrateFrom.id, toId: values.toId });
            await onRemoveDomain(migrateFrom.id);
            dispatchMessage({ content: t('Domain migrated and deleted successfully'), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t('Could not migrate or delete Domain');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <FormModal
            isOpen={isOpen}
            title={t('Delete Domain')}
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
                    label={t('Migrate existing data products & datasets')}
                    rules={[{ required: true, message: t('Please provide a value') }]}
                >
                    <Select>
                        {domains
                            .filter((domain) => domain.id !== migrateFrom.id)
                            .map((domain) => (
                                <Option key={domain.id} value={domain.id}>
                                    {domain.name}
                                </Option>
                            ))}
                    </Select>
                </Form.Item>
            </Form>
        </FormModal>
    );
}
