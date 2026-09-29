import { Button, Form, Input, Modal, Popconfirm, Select } from 'antd';
import { useTranslation } from 'react-i18next';

import {
    OutputPortAccessFunction,
    type OutputPortClassificationCreate,
    type OutputPortClassificationsGetItem,
    useCreateOutputPortClassificationMutation,
    useUpdateOutputPortClassificationMutation,
} from '@/store/api/services/generated/configurationOutputPortClassificationsApi.ts';
import {
    ACCESS_FUNCTION_ORDER,
    compareAccessFunctions,
    getAccessFunctionLabel,
} from '@/utils/access-function.helper.tsx';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    onClose: () => void;
    initial?: OutputPortClassificationsGetItem;
    isLastInviteOnly: boolean;
};

export function OutputPortClassificationFormModal({ onClose, initial, isLastInviteOnly }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm<OutputPortClassificationCreate>();
    const [createClassification, { isLoading: isCreating }] = useCreateOutputPortClassificationMutation();
    const [updateClassification, { isLoading: isUpdating }] = useUpdateOutputPortClassificationMutation();
    const accessFunction = Form.useWatch('access_function', form);

    const affectedOutputPorts = initial && accessFunction !== initial.access_function ? initial.output_port_count : 0;
    const loosensAccess =
        initial && accessFunction && compareAccessFunctions(accessFunction, initial.access_function) < 0;

    const handleFinish = async (values: OutputPortClassificationCreate) => {
        const result = initial
            ? await updateClassification({ id: initial.id, outputPortClassificationUpdate: values })
            : await createClassification(values);
        if (result.error) {
            return;
        }
        dispatchMessage({ content: t('Classification saved successfully'), type: 'success' });
        onClose();
    };

    return (
        <Modal
            open
            title={initial ? t('Update Classification') : t('Create new Classification')}
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
                    tooltip={isLastInviteOnly ? t('At least one classification must stay Invite only') : undefined}
                    rules={[{ required: true }]}
                >
                    <Select
                        disabled={isLastInviteOnly}
                        options={ACCESS_FUNCTION_ORDER.map((value) => ({
                            value,
                            label: getAccessFunctionLabel(t, value),
                        }))}
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
}
