import { Button, Form, Input, Modal } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDebouncedCallback } from 'use-debounce';
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import {
    type DomainCreate,
    type GetDomainsItem,
    useCreateDomainMutation,
    useUpdateDomainMutation,
} from '@/store/api/services/generated/configurationDomainsApi.ts';
import {
    ResourceNameModel,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
    useResourceNameConstraintsQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

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

    const [
        sanitizeResourceName,
        { data: sanitizedResourceName, isSuccess: sanitizedResourceNameSuccess, originalArgs: sanitizedName },
    ] = useLazySanitizeResourceNameQuery();
    const [validateResourceName] = useLazyValidateResourceNameQuery();
    const { data: constraints } = useResourceNameConstraintsQuery();
    const [canEditResourceName, setCanEditResourceName] = useState<boolean>(false);
    const domainNameValue = Form.useWatch('name', form);
    const fetchResourceNameDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), 500);

    useEffect(() => {
        if (mode === 'create' && !canEditResourceName) {
            form.setFields([{ name: 'namespace', validating: true, errors: [] }]);
            fetchResourceNameDebounced(domainNameValue ?? '');
        }
    }, [form, mode, canEditResourceName, domainNameValue, fetchResourceNameDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditResourceName && sanitizedResourceNameSuccess && sanitizedResourceName) {
            if (domainNameValue && sanitizedName === domainNameValue && !sanitizedResourceName.resource_name) {
                setCanEditResourceName(true);
            }
            form.setFieldValue('namespace', sanitizedResourceName.resource_name);
            form.validateFields(['namespace']);
        }
    }, [
        form,
        mode,
        canEditResourceName,
        domainNameValue,
        sanitizedName,
        sanitizedResourceName,
        sanitizedResourceNameSuccess,
    ]);

    const resourceNameValidationCallback = useCallback(
        (resourceName: string) =>
            validateResourceName({ resourceName: resourceName, model: ResourceNameModel.Domain }).unwrap(),
        [validateResourceName],
    );

    const handleFinish = async (values: DomainCreate) => {
        try {
            if (mode === 'create') {
                await createDomain(values).unwrap();
            } else {
                await editDomain({
                    id: initial?.id as string,
                    domainUpdate: values,
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
                    namespace: initial?.namespace,
                    description: initial?.description,
                }}
            >
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>

                <ResourceNameFormItem
                    form={form}
                    tooltip={t('The namespace of the Domain, used to name its resources. It cannot be changed later.')}
                    max_length={constraints?.max_length}
                    editToggleDisabled={mode === 'edit'}
                    canEditResourceName={canEditResourceName}
                    toggleCanEditResourceName={() => setCanEditResourceName((prev) => !prev)}
                    validationRequired={mode === 'create'}
                    validateResourceName={resourceNameValidationCallback}
                />

                <Form.Item
                    name="description"
                    label={t('Description')}
                    rules={[{ required: true, message: t('Please provide a description') }]}
                >
                    <Input />
                </Form.Item>
            </Form>
        </Modal>
    );
}
