import { Button, Form, Input, Modal, Popconfirm, Select } from 'antd';
import { useTranslation } from 'react-i18next';

import {
    OutputPortAccessFunction,
    type OutputPortAccessTypeCreate,
    type OutputPortAccessTypesGetItem,
    useCreateOutputPortAccessTypeMutation,
    useUpdateOutputPortAccessTypeMutation,
} from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import {
    ACCESS_FUNCTION_ORDER,
    compareAccessFunctions,
    getAccessFunctionInfo,
} from '@/utils/access-function.helper.tsx';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    onClose: () => void;
    initial?: OutputPortAccessTypesGetItem;
    isLastInviteOnly: boolean;
};

export function OutputPortAccessTypeFormModal({ onClose, initial, isLastInviteOnly }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm<OutputPortAccessTypeCreate>();
    const [createAccessType, { isLoading: isCreating }] = useCreateOutputPortAccessTypeMutation();
    const [updateAccessType, { isLoading: isUpdating }] = useUpdateOutputPortAccessTypeMutation();
    const accessFunction = Form.useWatch('access_function', form);

    const affectedOutputPorts =
        initial && accessFunction !== initial.access_function ? (initial.output_port_count ?? 0) : 0;
    const loosensAccess =
        initial && accessFunction && compareAccessFunctions(accessFunction, initial.access_function) < 0;

    const handleFinish = async (values: OutputPortAccessTypeCreate) => {
        const result = initial
            ? await updateAccessType({ id: initial.id, outputPortAccessTypeUpdate: values })
            : await createAccessType(values);
        if (result.error) {
            return;
        }
        dispatchMessage({ content: t('Access Type saved successfully'), type: 'success' });
        onClose();
    };

    return (
        <Modal
            open
            title={initial ? t('Update Access Type') : t('Create new Access Type')}
            onCancel={onClose}
            footer={[
                <Popconfirm
                    key="submit"
                    disabled={!affectedOutputPorts}
                    title={t('Change access function')}
                    description={
                        loosensAccess
                            ? t(
                                  'This loosens access for {{count}} Output Ports: users may get access with less or no approval.',
                                  { count: affectedOutputPorts },
                              )
                            : t('This changes the access function of {{count}} Output Ports.', {
                                  count: affectedOutputPorts,
                              })
                    }
                    onConfirm={() => form.submit()}
                    okText={t('Confirm')}
                    cancelText={t('Cancel')}
                >
                    <Button
                        type="primary"
                        loading={isCreating || isUpdating}
                        onClick={affectedOutputPorts ? undefined : () => form.submit()}
                    >
                        {initial ? t('Update') : t('Create')}
                    </Button>
                </Popconfirm>,
                <Button key="cancel" onClick={onClose}>
                    {t('Cancel')}
                </Button>,
            ]}
            centered
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={handleFinish}
                initialValues={initial ?? { description: '', access_function: OutputPortAccessFunction.Restricted }}
            >
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>
                <Form.Item name="description" label={t('Description')}>
                    <Input.TextArea />
                </Form.Item>
                <Form.Item
                    name="access_function"
                    label={t('Function')}
                    tooltip={isLastInviteOnly ? t('At least one access type must stay Invite only') : undefined}
                    rules={[{ required: true }]}
                >
                    <Select
                        disabled={isLastInviteOnly}
                        options={ACCESS_FUNCTION_ORDER.map((value) => ({
                            value,
                            label: getAccessFunctionInfo(t, value).label,
                        }))}
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
}
