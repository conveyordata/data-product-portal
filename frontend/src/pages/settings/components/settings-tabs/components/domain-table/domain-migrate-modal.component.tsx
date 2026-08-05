import { Button, Form, Input, Modal, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    type GetDomainsItem,
    useGetDomainsQuery,
    useMigrateDomainMutation,
    useRemoveDomainMutation,
} from '@/store/api/services/generated/configurationDomainsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

const { Option } = Select;

interface DomainMigrateFormValues {
    toId: string;
}

type Props = {
    onClose: () => void;
    isOpen: boolean;
    migrateFrom: GetDomainsItem;
};
export function CreateDomainMigrateModal({ isOpen, onClose, migrateFrom }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const { data: { domains = [] } = {} } = useGetDomainsQuery();
    const [migrateDomain] = useMigrateDomainMutation();
    const [onRemoveDomain] = useRemoveDomainMutation();

    const handleFinish = async (values: DomainMigrateFormValues) => {
        try {
            await migrateDomain({ fromId: migrateFrom.id, toId: values.toId }).unwrap();
            await onRemoveDomain(migrateFrom.id).unwrap();
            dispatchMessage({ content: t('Domain migrated and deleted successfully'), type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = t('Could not migrate or delete Domain');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <Modal
            open={isOpen}
            title={t('Delete Domain')}
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
            centered
        >
            <Form form={form} layout="vertical" onFinish={handleFinish} initialValues={migrateFrom}>
                <Form.Item name="name" label={t('Name')}>
                    <Input disabled />
                </Form.Item>

                <Form.Item
                    name="toId"
                    label={t('Migrate existing Data Products & Output Ports')}
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
        </Modal>
    );
}
