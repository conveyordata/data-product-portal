import { Button, Checkbox, Form, Input, InputNumber, Select } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useDebouncedCallback } from 'use-debounce';

import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import {
    useCreateDataProductSettingMutation,
    useGetDataProductSettingNamespaceLengthLimitsQuery,
    useLazyGetDataProductSettingNamespaceSuggestionQuery,
    useLazyValidateDataProductSettingNamespaceQuery,
    useUpdateDataProductSettingMutation,
} from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type {
    DataProductSettingContract,
    DataProductSettingScope,
    DataProductSettingType,
} from '@/types/data-product-setting';

import { useTranslation } from 'react-i18next';
import styles from './data-product-settings-table.module.scss';

const { Option } = Select;

type Mode = 'create' | 'edit';

const DEBOUNCE = 500;

interface DataProductSettingValueForm {
    name: string;
    namespace: string;
    id: string;
    tooltip: string;
    type: DataProductSettingType;
    default: boolean | string | string[];
    category: string;
    order: number;
}

interface SettingsFormText {
    title: string;
    successMessage: string;
    errorMessage: string;
    submitButtonText: string;
}

const createText = (t: TFunction, scope: DataProductSettingScope, mode: Mode): SettingsFormText => {
    if (mode === 'create') {
        if (scope === 'dataproduct') {
            return {
                title: t('Create New Data Product Setting'),
                successMessage: t('Data product setting created successfully'),
                errorMessage: t('Failed to create data product setting'),
                submitButtonText: t('Create'),
            };
        }
        return {
            title: t('Create New Dataset Setting'),
            successMessage: t('Dataset setting created successfully'),
            errorMessage: t('Failed to create dataset setting'),
            submitButtonText: t('Create'),
        };
    }
    if (scope === 'dataproduct') {
        return {
            title: t('Update Data Product Setting'),
            successMessage: t('Data product setting updated successfully'),
            errorMessage: t('Failed to update data product setting'),
            submitButtonText: t('Update'),
        };
    }
    return {
        title: t('Update Dataset Setting'),
        successMessage: t('Dataset setting updated successfully'),
        errorMessage: t('Failed to update dataset setting'),
        submitButtonText: t('Update'),
    };
};

const typeFormItem = (type: DataProductSettingType) => {
    switch (type) {
        case 'checkbox':
            return <Checkbox defaultChecked />;
        case 'tags':
            return <Select allowClear={false} defaultActiveFirstOption mode="tags" />;
        case 'input':
            return <Input />;
        default:
            return <Input />;
    }
};

const parseInitialDefaultValue = (initial: DataProductSettingContract) => {
    switch (initial.type) {
        case 'checkbox':
            return initial.default === 'true';
        case 'tags':
            return initial.default.split(',').filter((tag) => tag.length > 0);
        case 'input':
            return initial.default;
        default:
            return initial.default;
    }
};

const initialDefaultValue = (type: DataProductSettingType) => {
    switch (type) {
        case 'checkbox':
            return true;
        case 'tags':
            return [];
        case 'input':
            return '';
        default:
            return '';
    }
};

type Props = {
    onClose: () => void;
    isOpen: boolean;
    mode: Mode;
    scope: DataProductSettingScope;
    initial: DataProductSettingContract;
};
export function CreateSettingModal({ isOpen, onClose, scope, mode, initial }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();
    const [createDataProductSetting] = useCreateDataProductSettingMutation();
    const [updateDataProductSetting] = useUpdateDataProductSettingMutation();
    const typeValue = Form.useWatch<DataProductSettingType>('type', form);
    const nameValue = Form.useWatch<string>('name', form);

    const [fetchNamespace, { data: namespaceSuggestion }] = useLazyGetDataProductSettingNamespaceSuggestionQuery();
    const [validateNamespace] = useLazyValidateDataProductSettingNamespaceQuery();
    const { data: namespaceLengthLimits } = useGetDataProductSettingNamespaceLengthLimitsQuery();
    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);

    const initialValues = useMemo(() => {
        if (initial) {
            return {
                ...initial,
                default: parseInitialDefaultValue(initial),
            };
        }
        return { type: 'checkbox', default: initialDefaultValue(typeValue) };
    }, [initial, typeValue]);

    useEffect(() => {
        if (mode === 'create') {
            form.setFieldValue('default', initialDefaultValue(typeValue));
        }
    }, [form, typeValue, mode]);

    const variableText = createText(t, scope, mode);

    const handleFinish = async (values: DataProductSettingValueForm) => {
        try {
            if (mode === 'create') {
                const newSetting: DataProductSettingContract = {
                    ...values,
                    default: values.default.toString(),
                    scope: scope,
                    order: values.order,
                };
                await createDataProductSetting(newSetting);
            } else {
                const updateSetting: DataProductSettingContract = {
                    ...initial,
                    ...values,
                    default: values.default.toString(),
                };
                await updateDataProductSetting(updateSetting);
            }

            dispatchMessage({ content: variableText.successMessage, type: 'success' });
            form.resetFields();
            onClose();
        } catch (_) {
            dispatchMessage({ content: variableText.errorMessage, type: 'error' });
        }
    };

    const fetchNamespaceDebounced = useDebouncedCallback((name: string) => fetchNamespace(name), DEBOUNCE);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFields([
                {
                    name: 'namespace',
                    validating: true,
                    errors: [],
                },
            ]);
            fetchNamespaceDebounced(nameValue ?? '');
        }
    }, [mode, form, canEditNamespace, nameValue, fetchNamespaceDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFieldValue('namespace', namespaceSuggestion?.namespace);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditNamespace, namespaceSuggestion]);

    const validateNamespaceCallback = useCallback(
        (namespace: string) => validateNamespace({ namespace, scope }).unwrap(),
        [validateNamespace, scope],
    );

    return (
        <FormModal
            isOpen={isOpen}
            title={variableText.title}
            onClose={() => {
                form.resetFields();
                onClose();
            }}
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
        >
            <Form
                className={styles.form}
                form={form}
                layout="vertical"
                onFinish={handleFinish}
                initialValues={initialValues}
            >
                <Form.Item
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide a name') }]}
                >
                    <Input />
                </Form.Item>
                <NamespaceFormItem
                    form={form}
                    tooltip={t('The namespace of the setting')}
                    max_length={namespaceLengthLimits?.max_length}
                    editToggleDisabled={mode === 'edit'}
                    canEditNamespace={canEditNamespace}
                    toggleCanEditNamespace={() => setCanEditNamespace((prev) => !prev)}
                    validationRequired={mode === 'create'}
                    validateNamespace={validateNamespaceCallback}
                />
                <Form.Item
                    name="tooltip"
                    label={t('Tooltip')}
                    rules={[{ required: true, message: t('Please provide a tooltip') }]}
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    name="type"
                    label={t('Type')}
                    rules={[{ required: true, message: t('Please select a type') }]}
                >
                    <Select disabled={mode === 'edit'}>
                        <Option value="checkbox">{t('Checkbox')}</Option>
                        <Option value="tags">{t('List')}</Option>
                        <Option value="input">{t('Input')}</Option>
                    </Select>
                </Form.Item>

                <Form.Item
                    name="default"
                    label={t('Default Value')}
                    valuePropName={typeValue === 'checkbox' ? 'checked' : 'value'}
                    dependencies={['type']}
                >
                    {typeFormItem(typeValue)}
                </Form.Item>
                <Form.Item
                    name="category"
                    label={t('Category')}
                    rules={[{ required: true, message: t('Please provide a category') }]}
                    tooltip={t('The category breaks up the settings into sections')}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="order"
                    label={t('Order')}
                    rules={[
                        { required: true, message: t('Please provide an order') },
                        { type: 'integer', message: t('Order must be a number') },
                    ]}
                    tooltip={t('The order in which the setting will appear, within their own section')}
                >
                    <InputNumber className={styles.numberInput} min={0} precision={0} />
                </Form.Item>
            </Form>
        </FormModal>
    );
}
