import { Form, Modal, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { AccessModeSelector } from '@/components/data-products/technical-asset-form/access-mode-selector.component.tsx';
import type { AccessMode } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';

type Props = {
    outputPort: SearchOutputPortsResponseItem;
    onClose: () => void;
    selectAccessMode: (accessMode: AccessMode) => void;
};

type FormValues = {
    accessModes: string[];
};

export default function SelectAccessModeModal({ outputPort, onClose, selectAccessMode }: Props) {
    const [form] = Form.useForm();
    const { t } = useTranslation();
    return (
        <Modal title={t('Select an access mode')} onCancel={onClose} centered onOk={() => form.submit()} open>
            <Form
                form={form}
                layout="vertical"
                onFinish={(values: FormValues) => {
                    const selectedAccessMode = outputPort.access_modes.find(
                        (accessMode) => accessMode.id === values.accessModes[0],
                    );
                    if (!selectedAccessMode) {
                        throw new Error('Selected access mode not found');
                    }
                    selectAccessMode(selectedAccessMode);
                }}
            >
                <Typography.Paragraph>
                    {t(
                        "The Output Port {{name}} supports multiple access modes with different permissions. Choose the access mode you'd like to request.",
                        { name: outputPort.name },
                    )}
                </Typography.Paragraph>
                <Form.Item<FormValues>
                    name="accessModes"
                    label={t('Access mode')}
                    required
                    rules={[{ required: true, message: t('Please select an access mode') }]}
                >
                    <AccessModeSelector selectionMode="single" accessModes={outputPort.access_modes} />
                </Form.Item>
            </Form>
        </Modal>
    );
}
