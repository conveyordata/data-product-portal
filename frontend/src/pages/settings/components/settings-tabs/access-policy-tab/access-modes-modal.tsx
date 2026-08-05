import { Form, Input, Modal } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
    useCreateAccessModeMutation,
    useUpdateAccessModeMutation,
} from '@/store/api/services/generated/configurationAccessModesApi.ts';
import type { AccessMode } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

const { TextArea } = Input;

type Props = {
    onClose: () => void;
    editAccessMode?: AccessMode;
};
type AccessModeValues = {
    name: string;
    description: string;
};
export default function AccessModesModal({ editAccessMode, onClose }: Props) {
    const { t } = useTranslation();
    const mode = editAccessMode === undefined ? 'create' : 'edit';
    const [form] = Form.useForm<AccessModeValues>();

    const [createAccessMode] = useCreateAccessModeMutation();
    const [updateAccessMode] = useUpdateAccessModeMutation();
    const onFinish = useCallback(
        async (values: AccessModeValues) => {
            switch (mode) {
                case 'create':
                    await createAccessMode(values).unwrap();
                    onClose();
                    return;
                case 'edit': {
                    const { name, ...rest } = values;
                    await updateAccessMode({ id: editAccessMode?.id ?? '', accessModeUpdate: { ...rest } }).unwrap();
                    onClose();
                    return;
                }
            }
        },
        [mode, createAccessMode, updateAccessMode, editAccessMode, onClose],
    );

    return (
        <Modal
            centered
            title={mode === 'create' ? t('Create Access Mode') : t('Edit Access Mode')}
            open={true}
            onOk={() => form.submit()}
            onCancel={onClose}
        >
            <Form<AccessModeValues> form={form} layout="vertical" initialValues={editAccessMode} onFinish={onFinish}>
                <Form.Item<AccessModeValues>
                    name="name"
                    label={t('Name')}
                    required={mode === 'create'}
                    rules={[{ required: true, message: t('Please input the name of the access mode') }]}
                >
                    <Input placeholder="Name" disabled={mode === 'edit'} />
                </Form.Item>
                <Form.Item<AccessModeValues>
                    name="description"
                    label={t('Description')}
                    required
                    rules={[{ required: true, message: t('Please input the description of the access mode!') }]}
                >
                    <TextArea rows={4} />
                </Form.Item>
            </Form>
        </Modal>
    );
}
