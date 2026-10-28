import { Button, Form, Input, Modal, Select, Typography, theme } from 'antd';
import { Trans, useTranslation } from 'react-i18next';

import {
    OutputPortAccessFunction,
    type OutputPortAccessTypeCreate,
    type OutputPortAccessTypesGetItem,
    useCreateOutputPortAccessTypeMutation,
    useUpdateOutputPortAccessTypeMutation,
} from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import { ACCESS_FUNCTION_ORDER, getAccessFunctionInfo } from '@/utils/access-function.helper.tsx';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    onClose: () => void;
    initial?: OutputPortAccessTypesGetItem;
    isLastInviteOnly: boolean;
};

export function OutputPortAccessTypeFormModal({ onClose, initial, isLastInviteOnly }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const [form] = Form.useForm<OutputPortAccessTypeCreate>();
    const [modal, modalContextHolder] = Modal.useModal();
    const [createAccessType, { isLoading: isCreating }] = useCreateOutputPortAccessTypeMutation();
    const [updateAccessType, { isLoading: isUpdating }] = useUpdateOutputPortAccessTypeMutation();

    const outputPortCount = initial?.output_port_count ?? 0;

    const getAccessFunctionChangeConsequence = (
        from: OutputPortAccessFunction,
        to: OutputPortAccessFunction,
        count: number,
    ): string =>
        from === OutputPortAccessFunction.Private
            ? t('This will affect {{count}} Output Ports, which will become visible to the whole organisation.', {
                  count,
              })
            : {
                  [OutputPortAccessFunction.Unrestricted]: t(
                      'This will affect {{count}} Output Ports, whose access requests will be approved automatically.',
                      { count },
                  ),
                  [OutputPortAccessFunction.Restricted]: t(
                      'This will affect {{count}} Output Ports, whose access requests will need owner approval.',
                      { count },
                  ),
                  [OutputPortAccessFunction.Private]: t(
                      'This will affect {{count}} Output Ports, which will be hidden from everyone outside the owning team.',
                      { count },
                  ),
              }[to];

    const save = async (values: OutputPortAccessTypeCreate) => {
        const result = initial
            ? await updateAccessType({ id: initial.id, outputPortAccessTypeUpdate: values })
            : await createAccessType(values);
        if (result.error) {
            return;
        }
        dispatchMessage({ content: t('Access Type saved successfully'), type: 'success' });
        onClose();
    };

    const handleFinish = (values: OutputPortAccessTypeCreate) => {
        if (!initial || !outputPortCount || values.access_function === initial.access_function) {
            return save(values);
        }

        const content = (
            <>
                <Typography.Paragraph>
                    <Trans
                        t={t}
                        i18nKey="ConfirmAccessFunctionChange"
                        defaults="You are changing the function of <strong>{{name}}</strong> from <strong>{{from}}</strong> to <strong>{{to}}</strong>."
                        values={{
                            name: initial.name,
                            from: getAccessFunctionInfo(t, initial.access_function).label,
                            to: getAccessFunctionInfo(t, values.access_function).label,
                        }}
                        components={{ strong: <Typography.Text strong /> }}
                    />
                </Typography.Paragraph>
                <Typography.Text type="secondary">
                    {getAccessFunctionChangeConsequence(
                        initial.access_function,
                        values.access_function,
                        outputPortCount,
                    )}
                </Typography.Text>
            </>
        );

        const confirmation = modal.confirm({
            title: t('Confirm function change'),
            content: content,
            okText: t('Confirm change'),
            cancelText: t('Cancel'),
            centered: true,
            onOk: () => {
                confirmation.update({ cancelButtonProps: { disabled: true }, keyboard: false });
                return save(values);
            },
        });
    };

    return (
        <Modal
            open
            centered
            title={initial ? t('Update Access Type') : t('Create new Access Type')}
            onCancel={onClose}
            footer={[
                <Button key="cancel" onClick={onClose}>
                    {t('Cancel')}
                </Button>,
                <Button key="submit" type="primary" loading={isCreating || isUpdating} onClick={() => form.submit()}>
                    {initial ? t('Update') : t('Create')}
                </Button>,
            ]}
        >
            {modalContextHolder}
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
                <Form.Item
                    name="access_function"
                    label={t('Function')}
                    tooltip={isLastInviteOnly ? t('At least one access type must stay Invite only') : undefined}
                    extra={
                        outputPortCount && !isLastInviteOnly ? (
                            <Typography.Paragraph
                                type="secondary"
                                style={{
                                    marginTop: token.marginXXS,
                                    marginBottom: 0,
                                    paddingInlineStart: token.paddingXXS,
                                    fontSize: token.fontSizeSM,
                                }}
                            >
                                {t(
                                    'The function determines access-control behavior for Output Ports. Changing the function of an existing Access Type will trigger a confirmation step.',
                                )}
                            </Typography.Paragraph>
                        ) : undefined
                    }
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
                <Form.Item name="description" label={t('Description')}>
                    <Input.TextArea />
                </Form.Item>
            </Form>
        </Modal>
    );
}
