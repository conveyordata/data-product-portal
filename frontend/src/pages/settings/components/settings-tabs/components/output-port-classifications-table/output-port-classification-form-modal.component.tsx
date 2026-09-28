import { Button, Form, Input, Modal, Popconfirm, Select } from 'antd';
import { useTranslation } from 'react-i18next';

import {
    OutputPortAccessType,
    type OutputPortClassificationCreate,
    type OutputPortClassificationsGetItem,
    useCreateOutputPortClassificationMutation,
    useUpdateOutputPortClassificationMutation,
} from '@/store/api/services/generated/configurationOutputPortClassificationsApi.ts';
import { compareAccessFunctions, getAccessFunctionLabel } from '@/utils/access-type.helper.ts';
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
    const accessType = Form.useWatch('access_type', form);

    const affectedOutputPorts = initial && accessType !== initial.access_type ? initial.output_port_count : 0;
    const loosensAccess = initial && accessType && compareAccessFunctions(accessType, initial.access_type) < 0;

    const handleFinish = async (values: OutputPortClassificationCreate) => {
        try {
            if (initial) {
                await updateClassification({ id: initial.id, outputPortClassificationUpdate: values }).unwrap();
            } else {
                await createClassification(values).unwrap();
            }
            dispatchMessage({ content: t('Classification saved successfully'), type: 'success' });
            onClose();
        } catch (_e) {
            dispatchMessage({ content: t('Failed to save classification'), type: 'error' });
        }
    };

    const submitButton = (
        <Button
            key="submit"
            type="primary"
            loading={isCreating || isUpdating}
            onClick={affectedOutputPorts ? undefined : () => form.submit()}
        >
            {initial ? t('Update') : t('Create')}
        </Button>
    );

    return (
        <Modal
            open
            title={initial ? t('Update Classification') : t('Create new Classification')}
            onCancel={onClose}
            footer={[
                affectedOutputPorts ? (
                    <Popconfirm
                        key="submit"
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
                        {submitButton}
                    </Popconfirm>
                ) : (
                    submitButton
                ),
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
                initialValues={initial ?? { description: '', access_type: OutputPortAccessType.Restricted }}
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
                    name="access_type"
                    label={t('Access function')}
                    tooltip={isLastInviteOnly ? t('At least one classification must stay Invite only') : undefined}
                    rules={[{ required: true }]}
                >
                    <Select
                        disabled={isLastInviteOnly}
                        options={Object.values(OutputPortAccessType).map((value) => ({
                            value,
                            label: getAccessFunctionLabel(t, value),
                        }))}
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
}
