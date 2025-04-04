import { EditOutlined } from '@ant-design/icons';
import { Button, Checkbox, Form, Input, InputNumber, Select, Space } from 'antd';
import { TFunction } from 'i18next';
import { useEffect, useMemo, useState } from 'react';
import { useDebouncedCallback } from 'use-debounce';

import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import {
    useCreateDataProductSettingMutation,
    useGetDataProductSettingNamespaceLengthLimitsQuery,
    useLazyGetDataProductSettingNamespaceSuggestionQuery,
    useLazyValidateDataProductSettingNamespaceQuery,
    useUpdateDataProductSettingMutation,
} from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    DataProductSettingContract,
    DataProductSettingScope,
    DataProductSettingType,
} from '@/types/data-product-setting';
import { ValidationType } from '@/types/namespace/namespace';

import styles from './data-product-settings-table.module.scss';

const { Option } = Select;

type Mode = 'create' | 'edit';

const DEBOUNCE = 500;

interface CreateSettingModalProps {
    onClose: () => void;
    t: TFunction;
    isOpen: boolean;
    mode: Mode;
    scope: DataProductSettingScope;
    initial?: DataProductSettingContract;
}

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
        } else {
            return {
                title: t('Create New Dataset Setting'),
                successMessage: t('Dataset setting created successfully'),
                errorMessage: t('Failed to create dataset setting'),
                submitButtonText: t('Create'),
            };
        }
    } else {
        if (scope === 'dataproduct') {
            return {
                title: t('Update Data Product Setting'),
                successMessage: t('Data product setting updated successfully'),
                errorMessage: t('Failed to update data product setting'),
                submitButtonText: t('Update'),
            };
        } else {
            return {
                title: t('Update Dataset Setting'),
                successMessage: t('Dataset setting updated successfully'),
                errorMessage: t('Failed to update dataset setting'),
                submitButtonText: t('Update'),
            };
        }
    }
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

export const CreateSettingModal: React.FC<CreateSettingModalProps> = ({ isOpen, t, onClose, scope, mode, initial }) => {
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
        } else {
            return { type: 'checkbox', default: initialDefaultValue(typeValue) };
        }
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
                    ...initial!,
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
                <Form.Item label={t('Namespace')} required>
                    <Space.Compact direction="horizontal" className={styles.namespace}>
                        <Form.Item
                            name={'namespace'}
                            noStyle
                            hasFeedback
                            validateFirst
                            validateDebounce={DEBOUNCE}
                            rules={[
                                {
                                    required: canEditNamespace,
                                    message: t('Please input the namespace of the setting'),
                                },
                                {
                                    validator: async (_, value) => {
                                        if (mode === 'edit' || (!canEditNamespace && !value)) {
                                            return Promise.resolve();
                                        }

                                        const validationResponse = await validateNamespace({
                                            namespace: value.toLowerCase(),
                                            scope,
                                        }).unwrap();

                                        switch (validationResponse.validity) {
                                            case ValidationType.VALID:
                                                return Promise.resolve();
                                            case ValidationType.INVALID_LENGTH:
                                                return Promise.reject(new Error(t('Namespace is too long')));
                                            case ValidationType.INVALID_CHARACTERS:
                                                return Promise.reject(
                                                    new Error(t('Namespace contains invalid characters')),
                                                );
                                            case ValidationType.DUPLICATE_NAMESPACE:
                                                return Promise.reject(new Error(t('This namespace is already in use')));
                                            default:
                                                return Promise.reject(
                                                    new Error(t('Unknown namespace validation error')),
                                                );
                                        }
                                    },
                                },
                            ]}
                        >
                            <Input
                                disabled={!canEditNamespace}
                                showCount
                                maxLength={namespaceLengthLimits?.max_length}
                                onChange={(e) => {
                                    const lowerCaseValue = e.target.value.toLowerCase();
                                    form.setFieldValue('namespace', lowerCaseValue);
                                }}
                            />
                        </Form.Item>
                        <Button
                            disabled={mode === 'edit'}
                            onClick={() => setCanEditNamespace((prevState) => !prevState)}
                        >
                            <EditOutlined />
                        </Button>
                    </Space.Compact>
                </Form.Item>
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
};
