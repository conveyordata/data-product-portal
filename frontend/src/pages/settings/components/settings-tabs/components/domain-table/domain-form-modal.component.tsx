import { Button, Form, Input, Modal, Radio, Select } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type DomainCreate,
    type GetDomainsItem,
    useCreateDomainMutation,
    useUpdateDomainMutation,
} from '@/store/api/services/generated/configurationDomainsApi.ts';
import { useGetEnvironmentsQuery } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { selectFilterOptionByLabel } from '@/utils/form.helper.ts';

interface DomainFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

type Props = {
    onClose: () => void;
    isOpen: boolean;
    mode: 'create' | 'edit';
    initial?: GetDomainsItem;
};
export function CreateDomainModal({ isOpen, onClose, mode, initial }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const [createDomain] = useCreateDomainMutation();
    const [editDomain] = useUpdateDomainMutation();
    const { data: { environments: availableEnvironments = [] } = {} } = useGetEnvironmentsQuery();
    const environmentSelectOptions = availableEnvironments.map((environment) => ({
        label: environment.name,
        value: environment.id,
    }));
    const globalEnvironmentIds = availableEnvironments
        .filter((environment) => environment.is_global !== false)
        .map((environment) => environment.id);
    const [environmentMode, setEnvironmentMode] = useState<'global' | 'custom'>(
        initial?.environments.length ? 'custom' : 'global',
    );

    const createText: DomainFormText = {
        title: t('Create new Domain'),
        successMessage: t('Domain created successfully'),
        errorMessage: t('Failed to create Domain'),
        submitButtonText: t('Create'),
    };

    const updateText: DomainFormText = {
        title: t('Update Domain'),
        successMessage: t('Domain updated successfully'),
        errorMessage: t('Failed to update Domain'),
        submitButtonText: t('Update'),
    };

    const variableText = mode === 'create' ? createText : updateText;

    const handleFinish = async (values: DomainCreate) => {
        const payload = {
            ...values,
            environment_ids: environmentMode === 'global' ? [] : (values.environment_ids ?? []),
        };
        try {
            if (mode === 'create') {
                await createDomain(payload).unwrap();
            } else {
                await editDomain({
                    id: initial?.id as string,
                    domainUpdate: payload,
                }).unwrap();
            }

            dispatchMessage({ content: variableText.successMessage, type: 'success' });
            form.resetFields();
            onClose();
        } catch (_e) {
            const errorMessage = variableText.errorMessage;
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <Modal
            open={isOpen}
            title={variableText.title}
            onCancel={() => {
                form.resetFields();
                onClose();
            }}
            footer={[
                <Button key="submit" type="primary" onClick={() => form.submit()}>
                    {variableText.submitButtonText}
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
            centered
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={handleFinish}
                initialValues={{
                    name: initial?.name,
                    description: initial?.description,
                    environment_ids: initial?.environments.map((environment) => environment.id),
                }}
            >
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="description"
                    label={t('Description')}
                    rules={[{ required: true, message: t('Please provide a description') }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item label={t('Environment Setting')}>
                    <Radio.Group
                        block
                        optionType="button"
                        buttonStyle="solid"
                        value={environmentMode}
                        onChange={(e) => setEnvironmentMode(e.target.value)}
                        options={[
                            { label: t('Use global list'), value: 'global' },
                            { label: t('Use custom list'), value: 'custom' },
                        ]}
                    />
                </Form.Item>

                {environmentMode === 'global' ? (
                    <Form.Item label={t('Selected Environments')}>
                        <Select
                            mode="multiple"
                            value={globalEnvironmentIds}
                            options={environmentSelectOptions}
                            disabled
                        />
                    </Form.Item>
                ) : (
                    <Form.Item
                        name="environment_ids"
                        label={t('Selected Environments')}
                        rules={[{ required: true, message: t('Please select at least one environment') }]}
                    >
                        <Select
                            mode="multiple"
                            options={environmentSelectOptions}
                            showSearch={{ filterOption: selectFilterOptionByLabel }}
                        />
                    </Form.Item>
                )}
            </Form>
        </Modal>
    );
}
