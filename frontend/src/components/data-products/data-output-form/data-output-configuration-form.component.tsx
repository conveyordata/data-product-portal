import { Checkbox, Form, type FormInstance, Input, Radio, Select } from 'antd';
import type { Rule } from 'antd/es/form';
import type { BaseOptionType } from 'antd/es/select';
import { type ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { TechnicalMapping } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import type { UiElementMetadata } from '@/store/api/services/generated/pluginsApi';
import type { TechnicalAssetsCreateForm } from '@/types/technical-asset';
import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    form: FormInstance<TechnicalAssetsCreateForm>;
    namespace: string;
    technical_mapping: TechnicalMapping;
    configurationType: string;
    uiMetadataGroups: UiElementMetadata[];
    resultLabel: string;
    resultTooltip: string;
};

export function DataOutputConfigurationForm({
    form,
    namespace,
    technical_mapping,
    uiMetadataGroups,
    configurationType,
    resultLabel,
    resultTooltip,
}: Props) {
    const { t } = useTranslation();

    // Watch all form values at once - this ensures hooks are called unconditionally
    const allFormValues = Form.useWatch([], form) || {};

    // Build watched fields from form values
    const watchedFields: Record<string, unknown> = {};
    for (const field of uiMetadataGroups) {
        // biome-ignore lint: dynamic field names can't be statically typed at compile time
        watchedFields[field.name] = (allFormValues.configuration as any)?.[field.name];
    }

    // Auto-populate fields based on technical_mapping and namespace
    useEffect(() => {
        uiMetadataGroups.forEach((field) => {
            // Handle fields that should auto-populate from namespace when not source-aligned
            if (field.use_namespace_when_not_source_aligned) {
                form.setFieldValue(
                    // biome-ignore lint: dynamic field names can't be statically typed at compile time.
                    configurationFieldName(field.name) as any,
                    technical_mapping === 'default' ? namespace : undefined,
                );
            }
        });
    }, [form, technical_mapping, namespace, uiMetadataGroups]);

    if (!uiMetadataGroups) {
        return null;
    }

    const renderFormField = (fieldMetadata: UiElementMetadata) => {
        const {
            name,
            label,
            type,
            required,
            tooltip,
            hidden,
            depends_on,
            disabled,
            use_namespace_when_not_source_aligned,
            string,
            checkbox,
            select,
            radio,
        } = fieldMetadata;

        // Check if field should be hidden based on dependencies
        let isHidden = hidden;

        // Depends on can have multiple dependencies
        if (depends_on) {
            for (const dep of depends_on) {
                const dependentValue = watchedFields[dep.field_name];
                if (dependentValue !== dep.value) {
                    isHidden = true;
                    break;
                }
                isHidden = false;
            }
        }

        // Build validation rules
        const rules: Rule[] = [];
        if (required && !isHidden) {
            rules.push({
                required: true,
                message: t('Please provide {{ label }}', { label: label.toLowerCase() }),
            });
        }

        // Determine if field should be disabled
        const isDisabled = disabled || (use_namespace_when_not_source_aligned && technical_mapping === 'default');

        // Render the appropriate input component based on type
        let inputComponent: ReactElement;
        switch (type) {
            case 'checkbox':
                inputComponent = <Checkbox>{label}</Checkbox>;
                break;

            case 'select': {
                const selectOptions: BaseOptionType[] =
                    use_namespace_when_not_source_aligned && technical_mapping === 'default'
                        ? [namespace].map((val) => ({ label: val, value: val }))
                        : (select?.options?.map((option) => ({
                              label: option.label,
                              value: option.value.toString(),
                          })) ?? []);
                const maxCountGreaterThanOne = select?.max_count ? select?.max_count > 1 : false;
                inputComponent = (
                    <Select
                        allowClear
                        showSearch
                        mode={maxCountGreaterThanOne ? 'multiple' : undefined}
                        maxCount={maxCountGreaterThanOne ? (select?.max_count ?? 0) : undefined}
                        disabled={isDisabled ?? false}
                        options={selectOptions}
                    />
                );
                break;
            }
            case 'radio': {
                const radioOptions =
                    radio?.options?.map((option) => ({
                        label: option.label,
                        value: option.value.toString(),
                    })) ?? [];
                inputComponent = <Radio.Group disabled={isDisabled ?? false} options={radioOptions} />;
                break;
            }
            default:
                inputComponent = <Input />;
                break;
        }
        return (
            <ConfigurationFormItem
                key={name}
                name={name}
                label={type === 'checkbox' ? undefined : label}
                tooltip={tooltip ?? undefined}
                rules={rules}
                hidden={isHidden ?? false}
                valuePropName={type === 'checkbox' ? 'checked' : 'value'}
                initialValue={
                    type === 'string'
                        ? string?.initial_value
                        : type === 'checkbox'
                          ? checkbox?.initial_value
                          : type === 'radio'
                            ? radio?.initial_value
                            : undefined
                }
                required={type !== 'checkbox' && required && !isHidden}
            >
                {inputComponent}
            </ConfigurationFormItem>
        );
    };

    return (
        <ConfigurationSubForm
            form={form}
            configurationType={configurationType}
            resultLabel={resultLabel}
            resultTooltip={resultTooltip}
        >
            {uiMetadataGroups.map(renderFormField)}
        </ConfigurationSubForm>
    );
}
