import { Form, Input, Modal } from 'antd';
import { useTranslation } from 'react-i18next';

export type RevokeModal = {
    decisionNote: string;
};

type Props = {
    open: boolean;
    consumerName: string;
    onClose: () => void;
    onReject: (decisionNote: string) => void;
};

export function RevokeAccessModal({ onClose, onReject, open, consumerName }: Props) {
    const { t } = useTranslation();

    const [form] = Form.useForm<RevokeModal>();

    const handleOk = () => {
        form.submit();
    };

    const handleFinish = (values: RevokeModal) => {
        onReject(values.decisionNote);
    };

    return (
        <Modal
            title={t('Revoke access of {{consumerName}}', { consumerName })}
            open={open}
            onCancel={onClose}
            onOk={handleOk}
            okText={t('Confirm')}
            cancelText={t('Cancel')}
        >
            <Form form={form} layout="vertical" onFinish={handleFinish}>
                <Form.Item
                    name="decisionNote"
                    label={t('Decision note for revoking access')}
                    rules={[{ required: true, message: t('Please provide a decision note') }]}
                >
                    <Input.TextArea placeholder={t('Enter a decision note')} rows={4} />
                </Form.Item>
            </Form>
        </Modal>
    );
}
